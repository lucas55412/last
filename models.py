# 導入所需的模組
import os
import socket
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

def get_local_ip():
    """獲取本機IP地址"""
    try:
        # 取得本機IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return 'localhost'

# MongoDB 連接和資料庫會在運行時設置
client = None
db = None

def init_db(mongodb_uri):
    """初始化資料庫連接"""
    global client, db
    # 添加連接超時和錯誤重試設置，提高部署環境的連接穩定性
    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000,  # 5秒服務器選擇超時
        connectTimeoutMS=10000,         # 10秒連接超時
        socketTimeoutMS=20000,          # 20秒套接字超時
        retryWrites=True,               # 啟用寫入重試
        maxPoolSize=50,                 # 最大連接池大小
        minPoolSize=5                   # 最小連接池大小
    )
    db = client.flask_app
    
    # 測試資料庫連接
    try:
        # 執行簡單的 ping 命令來驗證連接
        client.admin.command('ping')
        print("✅ MongoDB 連接成功")
    except Exception as e:
        print(f"❌ MongoDB 連接失敗: {e}")
        raise

# User（用戶）集合操作類
class User:
    @classmethod
    def get_collection(cls):
        """獲取集合（相當於關聯式資料庫的表格）"""
        return None if db is None else db.users

    def __init__(self, username, email, password=None, created_at=None, _id=None):
        """
        初始化用戶物件
        參數:
            username: 用戶名稱
            email: 電子郵件
            password: 密碼（選填，用於註冊）
            created_at: 創建時間（若未提供則使用當前時間）
            _id: 用戶ID（可選）
        """
        self.username = username
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.created_at = created_at or datetime.utcnow()
        if _id:
            self._id = _id

    def save(self):
        """
        儲存用戶資料到資料庫
        返回:
            self: 儲存後的用戶物件
        """
        collection = self.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        if not hasattr(self, '_id'):
            # 準備要儲存的用戶資料
            user_data = {
                'username': self.username,
                'email': self.email,
                'password_hash': getattr(self, 'password_hash', None),
                'created_at': self.created_at
            }
            # 插入資料並獲取 ID
            result = collection.insert_one(user_data)
            self._id = result.inserted_id
        return self

    def check_password(self, password):
        """
        檢查密碼是否正確
        參數:
            password: 要檢查的密碼
        返回:
            bool: 密碼是否正確
        """
        password_hash = getattr(self, 'password_hash', None)
        if password_hash is None:
            return False
        return check_password_hash(password_hash, password)

    @classmethod
    def find_by_username(cls, username):
        """
        根據用戶名查找用戶
        參數:
            username: 要查找的用戶名
        返回:
            User 物件或 None
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        user_data = collection.find_one({'username': username})
        if user_data:
            user = cls(
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data['created_at']
            )
            user._id = user_data['_id']
            user.password_hash = user_data.get('password_hash')
            return user
        return None

    @classmethod
    def find_by_email(cls, email):
        """
        根據電子郵件查找用戶
        參數:
            email: 要查找的電子郵件
        返回:
            User 物件或 None
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        user_data = collection.find_one({'email': email})
        if user_data:
            user = cls(
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data['created_at']
            )
            user._id = user_data['_id']
            user.password_hash = user_data.get('password_hash')
            return user
        return None

    @classmethod
    def find_all(cls):
        """
        獲取所有用戶
        返回:
            用戶物件列表
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        return [cls(
            username=user_data['username'],
            email=user_data['email'],
            created_at=user_data['created_at']
        ) for user_data in collection.find()]

    @classmethod
    def find_by_id(cls, user_id):
        """
        根據ID查找用戶
        參數:
            user_id: 用戶ID
        返回:
            User 物件或 None
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        try:
            user_id = ObjectId(user_id)
            user_data = collection.find_one({'_id': user_id})
            if user_data:
                user = cls(
                    username=user_data['username'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    _id=user_data['_id']
                )
                user.password_hash = user_data.get('password_hash')
                return user
        except:
            return None
        return None

# Post（文章）集合操作類
class Post:
    @classmethod
    def get_collection(cls):
        """獲取集合"""
        return None if db is None else db.posts

    def __init__(self, title, content, user_id, created_at=None, _id=None):
        """
        初始化文章物件
        參數:
            title: 文章標題
            content: 文章內容
            user_id: 作者ID
            created_at: 創建時間（若未提供則使用當前時間）
            _id: 文章ID（可選）
        """
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        if _id:
            self._id = _id

    def save(self):
        """
        儲存文章到資料庫
        返回:
            self: 儲存後的文章物件
        """
        collection = self.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        if not hasattr(self, '_id'):
            # 準備要儲存的文章資料
            post_data = {
                'title': self.title,
                'content': self.content,
                'user_id': self.user_id,
                'created_at': self.created_at
            }
            # 插入資料並獲取 ID
            result = collection.insert_one(post_data)
            self._id = result.inserted_id
        return self

    @classmethod
    def find_all(cls):
        """
        獲取所有文章
        返回:
            文章物件列表
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        return [cls(
            title=post_data['title'],
            content=post_data['content'],
            user_id=post_data['user_id'],
            created_at=post_data['created_at'],
            _id=post_data['_id']
        ) for post_data in collection.find()]

    @classmethod
    def find_by_user_id(cls, user_id):
        """
        獲取特定用戶的所有文章
        參數:
            user_id: 用戶ID
        返回:
            文章物件列表
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        return [cls(
            title=post_data['title'],
            content=post_data['content'],
            user_id=post_data['user_id'],
            created_at=post_data['created_at'],
            _id=post_data['_id']
        ) for post_data in collection.find({'user_id': user_id})]

    @classmethod
    def find_by_id(cls, post_id):
        """
        根據ID查找文章
        參數:
            post_id: 文章ID
        返回:
            Post 物件或 None
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        try:
            post_id = ObjectId(post_id)
            post_data = collection.find_one({'_id': post_id})
            if post_data:
                return cls(
                    title=post_data['title'],
                    content=post_data['content'],
                    user_id=post_data['user_id'],
                    created_at=post_data['created_at'],
                    _id=post_data['_id']
                )
        except:
            return None
        return None

# MRTCarriage（捷運車廂）集合操作類
class MRTCarriage:
    @classmethod
    def get_collection(cls):
        """獲取集合"""
        return None if db is None else db.mrt_carriage

    def __init__(self, line_code=None, line_name=None, station_code=None, station_name=None, 
                 to_terminal=None, to_start=None, timestamp=None, _id=None):
        self.line_code = line_code
        self.line_name = line_name
        self.station_code = station_code
        self.station_name = station_name
        self.to_terminal = to_terminal
        self.to_start = to_start
        self.timestamp = timestamp
        if _id:
            self._id = _id

    def _parse_carriage_status(self, status_str):
        """解析車廂擁擠度字串"""
        if status_str is None or status_str == '----':
            return None
            
        # 將字串轉換為車廂列表
        carriages = list(str(status_str))
        
        # 計算每個車廂的擁擠程度
        carriage_status = []
        for level in carriages:
            try:
                # 將字符轉換為數字（1-3）
                level_num = int(level)
                # 根據級別計算百分比
                if level_num == 1:
                    percentage = 33.33  # 舒適
                elif level_num == 2:
                    percentage = 66.67  # 稍擁擠
                else:
                    percentage = 100    # 擁擠
                carriage_status.append(percentage)
            except ValueError:
                carriage_status.append(0)  # 無效數據
                
        return carriage_status
    
    @staticmethod
    def get_latest_by_line(line_code):
        """
        獲取特定路線的最新車廂資料
        參數:
            line_code: 路線代碼
        返回:
            MRTCarriage 物件列表
        """
        collection = MRTCarriage.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        # 獲取最新的時間戳
        latest = collection.find_one(
            {'line_code': line_code},
            sort=[('timestamp', -1)]
        )
        
        if latest is None:
            return []
        
        # 獲取該時間戳的所有資料
        results = collection.find({
            'line_code': line_code,
            'timestamp': latest['timestamp']
        })
        
        return [MRTCarriage(
            line_code=data['line_code'],
            line_name=data['line_name'],
            station_code=data['station_code'],
            station_name=data['station_name'],
            to_terminal=data['to_terminal'],
            to_start=data['to_start'],
            timestamp=data['timestamp'],
            _id=data['_id']
        ) for data in results]

# MRTStream（捷運人流）集合操作類
class MRTStream:
    @classmethod
    def get_collection(cls):
        """獲取集合"""
        return None if db is None else db.mrt_stream

    def __init__(self, count=None, timestamp=None, date=None, time=None, weekday=None, _id=None):
        self.count = count
        self.timestamp = timestamp
        self.date = date
        self.time = time
        self.weekday = weekday
        if _id:
            self._id = _id

    @staticmethod
    def get_daily_data(target_date=None):
        """
        獲取特定日期的人流量資料
        參數:
            target_date: 目標日期（可選）
        返回:
            MRTStream 物件列表
        """
        collection = MRTStream.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        # 如果沒有指定日期，使用最新的資料
        if target_date is None:
            latest = collection.find_one(sort=[('timestamp', -1)])
            if latest is not None:
                target_date = latest['date']
        
        # 查詢指定日期的資料
        results = collection.find({'date': target_date}).sort('timestamp')
        
        return [MRTStream(
            count=data['count'],
            timestamp=data['timestamp'],
            date=data['date'],
            time=data['time'],
            weekday=data['weekday'],
            _id=data['_id']
        ) for data in results]

# Comment（留言）集合操作類
class Comment:
    @classmethod
    def get_collection(cls):
        """獲取集合"""
        return None if db is None else db.comments

    def __init__(self, content, post_id, user_id, created_at=None):
        """
        初始化留言物件
        參數:
            content: 留言內容
            post_id: 文章ID
            user_id: 用戶ID
            created_at: 創建時間（若未提供則使用當前時間）
        """
        self.content = content
        self.post_id = post_id
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        """
        儲存留言到資料庫
        返回:
            self: 儲存後的留言物件
        """
        collection = self.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        if not hasattr(self, '_id'):
            # 準備要儲存的留言資料
            comment_data = {
                'content': self.content,
                'post_id': self.post_id,
                'user_id': self.user_id,
                'created_at': self.created_at
            }
            # 插入資料並獲取 ID
            result = collection.insert_one(comment_data)
            self._id = result.inserted_id
        return self

    @classmethod
    def find_by_post_id(cls, post_id):
        """
        獲取特定文章的所有留言
        參數:
            post_id: 文章ID
        返回:
            Comment 物件列表
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        return [cls(
            content=comment_data['content'],
            post_id=comment_data['post_id'],
            user_id=comment_data['user_id'],
            created_at=comment_data['created_at']
        ) for comment_data in collection.find({'post_id': post_id})]

    @classmethod
    def find_by_user_id(cls, user_id):
        """
        獲取特定用戶的所有留言
        參數:
            user_id: 用戶ID
        返回:
            Comment 物件列表
        """
        collection = cls.get_collection()
        if collection is None:
            raise RuntimeError("Database not initialized")
            
        return [cls(
            content=comment_data['content'],
            post_id=comment_data['post_id'],
            user_id=comment_data['user_id'],
            created_at=comment_data['created_at']
        ) for comment_data in collection.find({'user_id': user_id})] 