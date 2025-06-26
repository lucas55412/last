import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

# 1. 載入 .env 設定
load_dotenv("1.txt")

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"DATABASE={os.getenv('DB_NAME')};"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# 2. 指定所有 CSV 檔案
csv_files = [
    '/Users/lucas/Downloads/final-project-main/py/crawler/MRT_stream_data/2025-05-03-Saturday.csv',
    '/Users/lucas/Downloads/final-project-main/py/crawler/MRT_stream_data/2025-05-06-Tuesday.csv',
    '/Users/lucas/Downloads/final-project-main/py/crawler/MRT_stream_data/2025-05-07-Wednesday.csv',
    '/Users/lucas/Downloads/final-project-main/py/crawler/MRT_stream_data/2025-05-15-Thursday.csv',
]

# 3. 逐一讀檔、寫入資料庫
for csv_file in csv_files:
    print(f"正在處理 {csv_file}")
    df = pd.read_csv(csv_file)

    # 假設你的 csv 欄位已經是 date、timestamp、count
    for idx, row in df.iterrows():
        cursor.execute("""
            INSERT INTO mrt_stream ([date], [timestamp], [count])
            VALUES (?, ?, ?)
        """, (row['date'], row['timestamp'], int(row['count'])))
    conn.commit()
    print(f"✅ 匯入完成: {csv_file}")

conn.close()
print("✅ 所有 CSV 匯入完畢")

