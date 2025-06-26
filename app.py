# 導入所需的 Flask 相關模組
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# 導入自定義的資料模型
from models import User, Post, MRTCarriage, MRTStream, Comment, init_db
# 導入日期時間處理模組
from datetime import datetime
from functools import wraps
import os

# 配置：從環境變數讀取設置，如果沒有則使用默認值
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://william:Aa22303248@cluster0.mpwsv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
SECRET_KEY = os.environ.get('SECRET_KEY', 'b4fcc977cfcc1f1befbee58aecac6b5d3f710e09626bec8d02a3e90ad5579844')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# 初始化資料庫連接
init_db(MONGODB_URI)

# 創建 Flask 應用程式實例
app = Flask(__name__)
# 設定應用程式密鑰，用於會話管理和訊息閃現
app.secret_key = SECRET_KEY
app.debug = DEBUG

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
@app.route('/')
def index():
    """顯示所有文章的首頁"""
    # 獲取所有文章並按時間排序
    posts = Post.find_all()
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
    """
    顯示特定用戶的個人資料頁面
    參數:
        username: 用戶名稱
    """
    # 查找用戶
    user = User.find_by_username(username)
    if user:
        # 獲取該用戶的所有文章
        posts = Post.find_by_user_id(user._id)
        return render_template('user_profile.html', user=user, posts=posts)
    return redirect(url_for('index'))

# @app.route('/post/create'): 定義創建文章的路由
# methods=['GET', 'POST'] 表示這個路由可以處理 GET 和 POST 請求
# @login_required 確保只有登入用戶才能訪問此頁面
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """處理文章的創建"""
    if request.method == 'POST':
        # 從表單獲取文章資料
        title = request.form.get('title')
        content = request.form.get('content')
        
        # 使用當前登入用戶
        user_id = session['user_id']
        
        # 創建並儲存新文章
        post = Post(title=title, content=content, user_id=user_id)
        post.save()
        
        # 顯示成功訊息並重定向到首頁
        flash('文章發布成功！', 'success')
        return redirect(url_for('index'))
    
    # GET 請求時顯示創建文章的表單
    return render_template('create_post.html')

# @app.route('/login'): 定義登入頁面的路由
# methods=['GET', 'POST'] 允許顯示登入表單(GET)和處理登入請求(POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    if request.method == 'POST':
        # 從表單獲取用戶輸入的用戶名和密碼
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 查找用戶並驗證密碼
        user = User.find_by_username(username)
        if user and user.check_password(password):
            # 登入成功：將用戶資訊存儲到會話中
            session['user_id'] = str(user._id)
            session['username'] = user.username
            flash('登入成功！', 'success')
            return redirect(url_for('index'))
        
        # 登入失敗：顯示錯誤訊息
        flash('用戶名或密碼錯誤', 'danger')
    
    return render_template('login.html')

# @app.route('/register'): 定義註冊頁面的路由
# methods=['GET', 'POST'] 允許顯示註冊表單(GET)和處理註冊請求(POST)
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
        if User.find_by_username(username):
            flash('用戶名已被使用', 'danger')
            return render_template('register.html')
        
        # 檢查電子郵件是否已存在
        if User.find_by_email(email):
            flash('電子郵件已被使用', 'danger')
            return render_template('register.html')
        
        # 創建新用戶並保存到資料庫
        user = User(username=username, email=email, password=password)
        user.save()
        
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
    """獲取特定路線的車廂擁擠度資料，返回 JSON 格式"""
    data = MRTCarriage.get_latest_by_line(line_name)
    return jsonify([{
        'station_name': c.station_name,
        'to_terminal': c.to_terminal,  # 現在是一個包含6個值的列表
        'to_start': c.to_start,        # 現在是一個包含6個值的列表
        'station_code': c.station_code
    } for c in data])

@app.route('/api/mrt/stream')
def get_stream_data():
    """獲取捷運人流量資料，返回 JSON 格式"""
    data = MRTStream.get_daily_data()
    return jsonify([{
        'timestamp': c.time,  # 直接使用時間字串
        'count': c.count,
        'date': c.date,
        'weekday': c.weekday
    } for c in data])

@app.route('/post/<post_id>')
def view_post(post_id):
    """
    顯示特定文章的詳細內容和留言
    參數:
        post_id: 文章ID
    """
    # 查找文章
    post = Post.find_by_id(post_id)
    if post:
        # 獲取文章作者
        author = User.find_by_id(post.user_id)
        # 獲取文章的所有留言
        comments = Comment.find_by_post_id(post_id)
        # 獲取每個留言的作者資訊
        comment_authors = {str(comment.user_id): User.find_by_id(comment.user_id) for comment in comments}
        return render_template('view_post.html', post=post, author=author, comments=comments, comment_authors=comment_authors)
    return redirect(url_for('index'))

@app.route('/post/<post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """
    添加留言到特定文章
    參數:
        post_id: 文章ID
    """
    # 從表單獲取留言內容
    content = request.form.get('content')
    if content:
        # 創建新留言並保存到資料庫
        comment = Comment(
            content=content,
            post_id=post_id,
            user_id=session['user_id']  # 使用當前登入用戶的ID
        )
        comment.save()
        flash('留言發布成功！', 'success')
    else:
        flash('留言內容不能為空', 'danger')
    # 重定向回文章詳情頁面
    return redirect(url_for('view_post', post_id=post_id))

# 只在直接執行此檔案時運行應用程式
# 在生產環境中，通常由 WSGI 服務器（如 Gunicorn）來運行
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',                                    # 監聽所有網路介面
        port=int(os.environ.get('PORT', 8080)),           # 從環境變數獲取端口號
        debug=DEBUG                                        # 使用配置的調試模式
    ) 