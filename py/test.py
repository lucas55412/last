from app import get_db_connection  # 這行依你的 get_db_connection 定義位置修正

conn = get_db_connection()
cursor = conn.cursor()
print("== mrt_stream ==")
cursor.execute("SELECT TOP 5 * FROM mrt_stream")
for row in cursor.fetchall():
    print(row)
print("== mrt_carriage ==")
cursor.execute("SELECT TOP 5 * FROM mrt_carriage")
for row in cursor.fetchall():
    print(row)
conn.close()
