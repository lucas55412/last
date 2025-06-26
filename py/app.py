# 導入所需的 Flask 相關模組
from flask import *
# 導入自定義的資料模型
#from models import User, Post, MRTCarriage, MRTStream, Comment, init_db
from dotenv import load_dotenv
import pyodbc
# 導入import pymssql日期時間處理模組
from datetime import datetime
from functools import wraps
import os

load_dotenv("1.txt")
# 配置：從環境變數讀取設置，如果沒有則使用默認值
SECRET_KEY = os.environ.get('SECRET_KEY', 'b4fcc977cfcc1f1befbee58aecac6b5d3f710e09626bec8d02a3e90ad5579844')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'



# 初始化資料庫連接

# 創建 Flask 應用程式實例
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# 設定應用程式密鑰，用於會話管理和訊息閃現
app.secret_key = SECRET_KEY
app.debug = DEBUG


def dictfetchone(cursor):
    """將 fetchone 結果轉為 dict"""
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def fetch_all_as_dict(cursor):
    """將 pyodbc 查詢結果轉換為 list[dict]"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"DATABASE={os.getenv('DB_NAME')};"
    )
    return pyodbc.connect(conn_str)


# 登入要求裝飾器：檢查用戶是否已登入，如果未登入則重定向到登入頁面
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# @app.route('/'): 定義根路由，處理網站首頁的訪問
# methods 默認為 ['GET']，表示只接受 GET 請求

def find_all_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cursor.fetchall()
    conn.close()
    return posts

from datetime import datetime

from datetime import datetime

def get_daily_data(target_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 先查今天最新日期
    if target_date is None:
        cursor.execute("SELECT TOP 1 [date] FROM mrt_stream ORDER BY [timestamp] DESC")
        row = cursor.fetchone()
        
        if row:
            target_date = row[0]
        else:
            conn.close()
            return []

    print("DEBUG: 查詢日期", target_date)
    
    cursor.execute("""
        SELECT [date], [timestamp], [count]
        FROM mrt_stream
        WHERE [date] = ?
        ORDER BY [timestamp]
    """, (target_date,))

    rows = cursor.fetchall()
    conn.close()

    # ✅ 把時間部分的 datetime(1900-01-01, HH:MM:SS) 合併到正確的 date
    processed_rows = []
    for date_part, time_part, count in rows:
        # 無論 time_part 是字串還是 datetime，先轉成 datetime 後取出時間
        if isinstance(time_part, str):
            time_obj = datetime.strptime(time_part, '%Y-%m-%d %H:%M:%S').time()
        else:
            time_obj = time_part.time()

        # 將 date_part 和 time_part 合併成完整 timestamp
        full_ts = datetime.combine(date_part, time_obj)
        processed_rows.append((date_part, full_ts, count))

    return processed_rows

def find_by_id(post_id):
    """
    根據 ID 查找文章（使用 MSSQL)
    參數:
        post_id: 整數型文章 ID
    返回:
        dict 或 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'user_id': row[3],
                'created_at': row[4]
            }
        else:
            return None

    except Exception as e:
        print(f"❌ 查詢發生錯誤: {e}")
        return None

def find_user_by_username(username):
    """
    根據用戶名查找用戶（使用 MSSQL)
    參數:
        username: 要查找的使用者名稱
    返回:
        dict 或 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'created_at': user_data['created_at'],
                'password_hash': user_data.get('password_hash')
            }
        else:
            return None

    except Exception as e:
        print(f"❌ 查詢失敗：{e}")
        return None
    
def save_comment(content, post_id, user_id, created_at=None):
    try:
        if created_at is None:
            created_at = datetime.utcnow()
        # 轉成SQL接受的字串格式
        created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO comments (content, post_id, user_id, created_at)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
        """, (content, post_id, user_id, created_at_str))  # 直接傳字串

        inserted_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return {
            'id': inserted_id,
            'content': content,
            'post_id': post_id,
            'user_id': user_id,
            'created_at': created_at_str
        }

    except Exception as e:
        print(f"❌ 留言儲存失敗：{e}")
        return None
def find_comments_by_post_id(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE post_id = ?", (post_id,))
    
    # ✅ 包成 list of dict（否則就只能用 row[0]、row[1] 存取）
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    comments = [dict(zip(columns, row)) for row in rows]
    
    conn.close()
    return comments

def get_latest_by_line(conn, line_code):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT TOP 1 timestamp
            FROM mrt_carriage
            WHERE line_id = ?
            ORDER BY timestamp DESC
        """, (line_code,))
        row = cursor.fetchone()

        if row is None:
            return []

        latest_timestamp = row[0]  # 因為是 tuple，不是 dict

        cursor.execute("""
            SELECT *
            FROM mrt_carriage
            WHERE line_id = ? AND timestamp = ?
        """, (line_code, latest_timestamp))

        columns = [column[0] for column in cursor.description]
        results = []
        from datetime import datetime
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if isinstance(row_dict['timestamp'], datetime):
                row_dict['timestamp'] = row_dict['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            results.append(row_dict)
        return results


@app.route('/')
def index():
    posts = find_all_posts()
    try:
        posts = find_all_posts()
    except Exception as e:
        print("❌ 讀取文章失敗：", e)
        posts = []
    return render_template('index.html', posts=posts)


# @app.route('/about'): 定義關於頁面的路由
# 當用戶訪問 /about 時顯示關於頁面
@app.route('/about')
def about():
    """顯示關於頁面"""
    return render_template('about.html')

# @app.route('/user/<username>'): 定義用戶資料頁面的路由
# <username> 是一個 URL 變數，會被傳遞給視圖函數
@app.route('/user/<username>')
def user_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        flash("找不到使用者", "danger")
        return redirect(url_for('index'))  # ✅ 這裡 return 結束函式

    # ✅ 這段只在 row 存在的時候才執行
    from datetime import datetime
    user_data = {
        'id': row.id,
        'username': row.username,
        'email': row.email,
        'created_at': row.created_at or datetime.utcnow()
    }

    return render_template('user_profile.html', user=user_data)

@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = session['user_id']
        created_at = datetime.utcnow()  # ✅ 用 datetime 類型，讓資料庫存成 datetime，不要轉字串


        conn = get_db_connection()
        cursor = conn.cursor()

        # 使用 OUTPUT INSERTED.id 回傳新文章的 id
        cursor.execute(
            """
            INSERT INTO posts (title, content, user_id, created_at)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            (title, content, user_id, created_at)
        )

        result = cursor.fetchone()
        post_id = result[0] if result else None

        conn.commit()
        conn.close()

        if post_id is None:
            flash("❌ 發布文章失敗，未能取得文章 ID", "danger")
            return redirect(url_for('index'))

        flash('✅ 文章發布成功！', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    return render_template('create_post.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        # ✅ 必須先轉成 dict，再關閉 cursor
        user_check = None
        if row:
            columns = [desc[0] for desc in cursor.description]
            user_check = dict(zip(columns, row))

        conn.close()

        if user_check and password == user_check['password']:
            session['user_id'] = user_check['id']  # ✅ 注意這裡是 id，不是 user_id
            session['username'] = user_check['username']
            flash('登入成功！', 'success')
            return redirect(url_for('index'))

        flash('用戶名或密碼錯誤', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """處理用戶註冊"""
    if request.method == 'POST':
        # 從表單獲取註冊資料
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 驗證密碼：檢查兩次輸入的密碼是否一致
        if password != confirm_password:
            flash('兩次輸入的密碼不一致', 'danger')
            return render_template('register.html')
        
        # 檢查用戶名是否已存在
       
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_check = cursor.fetchone()
        conn.close()
        if user_check :
            flash('用戶名已被使用', 'danger')
            return render_template('register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        email_check = cursor.fetchone()
        conn.close()
        # 檢查電子郵件是否已存在
        if email_check:
            flash('電子郵件已被使用', 'danger')
            return render_template('register.html')
        
        # 創建新用戶並保存到資料庫
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password,email) VALUES (?, ?,?)", (username, password,email,))
        conn.commit()
        conn.close()

        """user = User(username=username, email=email, password=password)
        user.save()"""
        
        # 註冊成功，重定向到登入頁面
        flash('註冊成功！請登入', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# @app.route('/logout'): 定義登出路由
# 不需要 methods 參數，因為只處理 GET 請求
@app.route('/logout')
def logout():
    """處理用戶登出"""
    # 清除所有會話資料
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))

# 捷運資料相關路由
@app.route('/mrt')
def mrt_dashboard():
    """顯示捷運資料儀表板"""
    return render_template('mrt_dashboard.html')


@app.route('/api/mrt/carriage/<line_name>')
def get_carriage_data(line_name):
    try:
        conn = get_db_connection()
        data = get_latest_by_line(conn, line_name)
        conn.close()
        print(data)
        
        # ⭐⭐⭐ 關鍵修正！加這段
        
        print("DEBUG: data type =", type(data))
        for i, row in enumerate(data):
            print(f"DEBUG: row[{i}] type = {type(row)}, value = {row}")
        from datetime import datetime
        for row in data:
            if isinstance(row.get('timestamp'), datetime):
                row['timestamp'] = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(data)
    
    except Exception as e:
        print(f"❌ 錯誤發生：{e}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500





from datetime import datetime

from datetime import datetime

@app.route('/api/mrt/stream')
def get_stream_data():
    data = get_daily_data()

    # ✅ 印出前五筆資料做 debug 檢查
    for i, row in enumerate(data[:5]):
        print(f"✅ DEBUG 檢查資料[{i}]:", row)
        print(f"📅 timestamp 資料型別: {type(row[1])}")

    # ✅ 回傳 JSON 格式：ISO 格式日期 + 格式化時間字串
    return jsonify([
        {
            "date": row[0].isoformat(),  # ✅ ex: 2025-06-26
            "timestamp": row[1].strftime('%Y-%m-%d %H:%M:%S'),  # ✅ ex: 2025-06-26 08:30:00
            "count": row[2]
        }
        for row in data
    ])

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    user_id = session.get('user_id')

    if content and user_id:
        save_comment(content, post_id, user_id)
        flash("留言已新增", "success")
    else:
        flash("留言內容不得為空", "danger")

    return redirect(url_for('view_post', post_id=post_id))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """
    顯示特定文章的詳細內容和留言
    參數:
        post_id: 文章ID
    """
    # 查找文章（確保回傳 dict）
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = dictfetchone(cursor)
    conn.close()

    if post:
        # 獲取文章作者
        author = find_user_by_username(post['user_id'])

        # 獲取文章的所有留言（你原本的函式可保留）
        comments = find_comments_by_post_id(post_id)

        # 獲取每個留言的作者資訊（這裡 comments 建議是 list of dict）
        comment_authors = {
        comment['user_id']: find_user_by_username(comment['user_id']) for comment in comments}

        return render_template('view_post.html', post=post, author=author, comments=comments, comment_authors=comment_authors)

    return redirect(url_for('index'))


def save_comment(content, post_id, user_id):
    """將留言儲存到 comments 表中"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (content, post_id, user_id, created_at)
            VALUES (?, ?, ?, GETDATE())
        """, (content, post_id, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 儲存留言時發生錯誤: {e}")
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',                                    # 監聽所有網路介面
        port=int(os.environ.get('PORT', 8080)),           # 從環境變數獲取端口號
        debug=DEBUG                                        # 使用配置的調試模式
    )