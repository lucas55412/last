import pyodbc
from dotenv import load_dotenv
import os

# 指定 .env 檔案的正確路徑（在上層資料夾）
load_dotenv("1.txt")
# 檢查是否讀到資料
print("📁 Current dir:", os.getcwd())
print("🔍 DB_SERVER:", os.getenv("DB_SERVER"))
print("🔍 DB_USER:", os.getenv("DB_USER"))
print("🔍 DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("🔍 DB_NAME:", os.getenv("DB_NAME"))

# 建立連線
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"DATABASE={os.getenv('DB_NAME')}"
)

conn = pyodbc.connect(conn_str)

print("✅ 成功連線 MSSQL")

cursor = conn.cursor()

# 建立 users 表（如果不存在）
cursor.execute("""
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='users' AND xtype='U'
)
BEGIN
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(255),
        password NVARCHAR(255),
        email NVARCHAR(255),
        user_id NVARCHAR(255)
    )
END
""")

try:
    cursor.execute("SELECT created_at FROM users")
    print("✅ `created_at` 欄位已存在")
except pyodbc.ProgrammingError:
    print("⚠️ 沒有 `created_at` 欄位，新增中...")
    cursor.execute("""
        ALTER TABLE users
        ADD created_at DATETIME DEFAULT GETDATE()
    """)
    conn.commit()
    print("✅ `created_at` 欄位新增完成")


# 建立 posts 表（如果不存在）
cursor.execute("""
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='posts' AND xtype='U'
)
BEGIN
    CREATE TABLE posts (
        id INT PRIMARY KEY IDENTITY(1,1),
        title NVARCHAR(MAX),
        content NVARCHAR(MAX),
        user_id NVARCHAR(255),
        created_at DATETIME DEFAULT GETDATE()
    )
END
""")

# 可以加更多資料表建立...

conn.commit()
conn.close()

print("✅ 資料表初始化完成")
