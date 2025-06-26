import os
import csv
from datetime import datetime
from pymongo import MongoClient
from models import db  # 使用已經設定好的 MongoDB 連接

def import_carriage_data():
    """匯入捷運車廂擁擠度資料"""
    # 清空現有集合
    db.mrt_carriage.drop()
    
    # 定義路線名稱對應
    line_codes = {
        '板南線': 'BL',
        '淡水信義線': 'R',
        '松山新店線': 'G',
        '中和新蘆線': 'O',
        '文湖線': 'BR'
    }
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'crawler', 'MRT_carriage_data')
    
    total_records = 0
    for line_name, line_code in line_codes.items():
        line_dir = os.path.join(data_dir, line_name)
        if not os.path.exists(line_dir):
            print(f"⚠️ 找不到 {line_name} 的資料夾")
            continue
            
        print(f"正在處理 {line_name} 的資料...")
        for file_name in os.listdir(line_dir):
            if not file_name.endswith('.csv'):
                continue
                
            file_path = os.path.join(line_dir, file_name)
            # 從檔名解析日期 (格式: YYYY-MM-DD-Weekday.csv)
            date_str = '-'.join(file_name.split('-')[:3])  # 取得 YYYY-MM-DD 部分
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                current_time = None
                batch_data = []
                
                for row in reader:
                    if not row:  # 跳過空行
                        continue
                        
                    if row[0].startswith('=='):
                        # 更新時間戳記
                        time_str = row[0].strip('=')
                        try:
                            current_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                        except ValueError as e:
                            print(f"⚠️ 跳過無效的時間格式: {date_str} {time_str}")
                            continue
                    elif len(row) == 4 and not row[0].startswith('---'):
                        # 確保有有效的時間戳記
                        if not current_time:
                            continue
                            
                        # 資料行
                        try:
                            to_terminal = float(row[2]) if row[2] != '----' else None
                            to_start = float(row[3]) if row[3] != '----' else None
                        except ValueError:
                            print(f"⚠️ 跳過無效的擁擠度數據: {row}")
                            continue
                            
                        document = {
                            'line_code': line_code,
                            'line_name': line_name,
                            'station_code': row[0],
                            'station_name': row[1],
                            'to_terminal': to_terminal,
                            'to_start': to_start,
                            'timestamp': current_time
                        }
                        batch_data.append(document)
                
                if batch_data:
                    try:
                        db.mrt_carriage.insert_many(batch_data)
                        total_records += len(batch_data)
                        print(f"✅ 已匯入 {file_name} 的資料")
                    except Exception as e:
                        print(f"❌ 匯入 {file_name} 時發生錯誤: {str(e)}")
                    
    print(f"✅ 已匯入 {total_records} 筆車廂擁擠度資料")

def import_stream_data():
    """匯入捷運人流量資料"""
    print("\n開始匯入人流量資料...")
    
    # 清空現有集合
    db.mrt_stream.drop()
    print("✓ 已清空舊有資料")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'crawler', 'MRT_stream_data')
    
    if not os.path.exists(data_dir):
        print("⚠️ 找不到人流量資料夾")
        return
    
    print(f"✓ 找到資料目錄: {data_dir}")
    
    total_records = 0
    processed_files = 0
    
    # 列出所有CSV檔案
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"✓ 找到 {len(csv_files)} 個CSV檔案")
    
    for file_name in csv_files:
        file_path = os.path.join(data_dir, file_name)
        print(f"\n處理檔案: {file_name}")
        
        batch_data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 讀取並解析CSV標頭
                header = f.readline().strip().split(',')
                if not all(field in header for field in ['date', 'timestamp', 'count']):
                    print(f"⚠️ 檔案格式不正確: {file_name}")
                    continue
                
                # 重置檔案指標並跳過標頭
                f.seek(0)
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # 清理並驗證資料
                        date_str = row['date'].strip()
                        time_str = row['timestamp'].strip()
                        count_str = row['count'].strip()
                        
                        # 驗證日期格式
                        if not (date_str and time_str):
                            print(f"⚠️ 無效的日期或時間: {date_str} {time_str}")
                            continue
                        
                        # 解析時間戳記
                        timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                        
                        # 解析人流量
                        count = int(count_str)
                        
                        # 建立文件
                        document = {
                            'date': date_str,
                            'time': time_str,
                            'timestamp': timestamp,
                            'count': count,
                            'weekday': timestamp.strftime('%A')  # 新增星期幾的資訊
                        }
                        batch_data.append(document)
                        
                    except ValueError as e:
                        print(f"⚠️ 資料解析錯誤: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"⚠️ 未預期的錯誤: {str(e)}")
                        continue
            
            # 批次寫入資料庫
            if batch_data:
                try:
                    result = db.mrt_stream.insert_many(batch_data)
                    inserted_count = len(result.inserted_ids)
                    total_records += inserted_count
                    processed_files += 1
                    print(f"✅ 成功匯入 {inserted_count} 筆記錄")
                except Exception as e:
                    print(f"❌ 資料庫寫入錯誤: {str(e)}")
            
        except Exception as e:
            print(f"❌ 檔案處理錯誤: {str(e)}")
            continue
    
    print(f"\n匯入摘要:")
    print(f"✓ 處理了 {processed_files}/{len(csv_files)} 個檔案")
    print(f"✓ 總共匯入 {total_records} 筆人流量記錄")
    
    # 驗證資料
    try:
        actual_count = db.mrt_stream.count_documents({})
        print(f"✓ 資料庫中實際記錄數: {actual_count}")
        
        # 顯示最新的資料時間範圍
        latest = db.mrt_stream.find_one(sort=[('timestamp', -1)])
        earliest = db.mrt_stream.find_one(sort=[('timestamp', 1)])
        if latest and earliest:
            print(f"✓ 資料時間範圍: {earliest['timestamp']} 到 {latest['timestamp']}")
        
    except Exception as e:
        print(f"❌ 資料驗證錯誤: {str(e)}")

def create_indexes():
    """建立索引以提升查詢效能"""
    # 車廂擁擠度資料的索引
    db.mrt_carriage.create_index([
        ('line_code', 1),
        ('timestamp', -1)
    ])
    
    # 人流量資料的索引
    db.mrt_stream.create_index('timestamp')
    
    print("✅ 索引建立完成")

if __name__ == "__main__":
    print("開始匯入捷運資料到 MongoDB...")
    import_carriage_data()
    import_stream_data()
    create_indexes()
    print("資料匯入完成！") 