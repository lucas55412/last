import os
import csv
from datetime import datetime
import pyodbc
from dotenv import load_dotenv
def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.tables")
    print("🟢 目前 DB 的所有資料表：", [r[0] for r in cursor.fetchall()])
    cursor.close()
    return conn

# ✅ 從 2.txt 載入環境變數
load_dotenv("1.txt")
def init_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 建立 mrt_stream 表（加上 count INT 欄位）
    cursor.execute("""
    IF NOT EXISTS (
        SELECT * FROM sysobjects WHERE name='mrt_stream' AND xtype='U'
    )
    BEGIN
        CREATE TABLE mrt_stream (
            date DATE,
            timestamp DATETIME,
            count INT              -- ← ★ 新增這一行！
        )
    END
    """)

    # ...（下略）

    conn.commit()
    conn.close()
    print("✅ 資料表初始化完成")

# ✅ 路線對照
line_codes = {
    '板南線': 'BL',
    '淡水信義線': 'R',
    '松山新店線': 'G',
    '中和新蘆線': 'O',
    '文湖線': 'BR'
}

# ✅ pyodbc 資料庫連線
def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def import_stream_data():
    print("🚇 匯入人流量資料 mrt_stream...")
    base_dir = 'crawler/MRT_stream_data'
    conn = get_db_connection()
    cursor = conn.cursor()

    for file in os.listdir(base_dir):
        if file.endswith('.csv'):
            with open(os.path.join(base_dir, file), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        date = row['date'].strip()
                        timestamp = row['timestamp'].strip()
                        count = int(row['count'])
                        # 你 csv 如果有其他欄位，這裡再調整
                        cursor.execute("""
                            INSERT INTO mrt_stream ([date], [timestamp], [count])
                            VALUES (?, ?, ?)
                        """, (date, timestamp, count))
                    except Exception as e:
                        print(f"⚠️ 跳過錯誤: {e}")
    conn.commit()
    conn.close()
    print("✅ mrt_stream 資料匯入完成\n")

def import_carriage_data():
    print("🚈 匯入車廂擁擠度資料 mrt_carriage...")
    base_dir = 'crawler/MRT_carriage_data'
    conn = get_db_connection()   # 這裡只呼叫一次
    cursor = conn.cursor()

    for line_name, line_code in line_codes.items():
        line_dir = os.path.join(base_dir, line_name)
        if not os.path.exists(line_dir):
            print(f"❌ 找不到資料夾: {line_name}")
            continue

        for file in os.listdir(line_dir):
            if not file.endswith('.csv'):
                continue

            date_str = '-'.join(file.split('-')[:3])
            file_path = os.path.join(line_dir, file)
            with open(file_path, encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳過表頭

                current_time = None
                for row in reader:
                    if not row:
                        continue
                    if row[0].startswith('=='):
                        try:
                            current_time = datetime.strptime(f"{date_str} {row[0].strip('=')}", "%Y-%m-%d %H:%M:%S")
                        except Exception as e:
                            print(f"⚠️ 跳過時間: {row[0]} 原因: {e}")
                            continue
                    elif len(row) == 4 and not row[0].startswith('---'):
                        # 只處理全部是數字的欄位
                        if not row[2].isdigit() or not row[3].isdigit():
                            continue
                        try:
                            station = row[1]
                            carriage_number = int(row[2])
                            crowd_level = int(row[3])

                            cursor.execute("""
                                INSERT INTO mrt_carriage (line_id, station, carriage_number, crowd_level, [timestamp])
                                VALUES (?, ?, ?, ?, ?)
                            """, (line_code, station, carriage_number, crowd_level, current_time))
                        except Exception as e:
                            print(f"⚠️ 跳過: {row} 原因: {e}")

    conn.commit()    # 放在整個 for loop 結束後
    conn.close()     # 放在最外層
    print("✅ mrt_carriage 資料匯入完成\n")



if __name__ == "__main__":
    init_tables()
    import_stream_data()
    import_carriage_data()
    print("🎉 所有資料匯入完成！")


