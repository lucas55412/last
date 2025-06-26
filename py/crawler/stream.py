import requests
import csv
from datetime import datetime
import os
from dateutil import parser
import traceback
import time

now = datetime.now()
if now.second < 10:
    time_to_wait = 10 - now.second
    time.sleep(time_to_wait)

# 設定資料夾與日誌路徑
BASE_DIR = "/Users/angelina1114/Desktop/Final_report"
DATA_FOLDER = f"{BASE_DIR}/MRT_stream_data"
LOG_FOLDER = f"{DATA_FOLDER}/logs"

def crawl_data():
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    url = (
        f"https://citydashboard.taipei/api/v1/component/73/chart"
        f"?city=taipei&timefrom={today}T00:00:00%2B08:00&timeto={today}T{now}%2B08:00"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 如果回傳不是200會直接拋錯
    data = response.json()

    results = []

    for point in data["data"][0]["data"]:
        time = point["x"]
        count = point["y"]

        dt = parser.isoparse(time)
        formatted_time = dt.strftime("%H:%M:%S")
        formatted_date = dt.strftime("%Y-%m-%d")

        results.append((formatted_date, formatted_time, count))

    return results

def save_to_csv(data):
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A") 

    os.makedirs(DATA_FOLDER, exist_ok=True)

    file_path = f"{DATA_FOLDER}/{today}-{weekday}.csv"

    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "timestamp", "count"])
        writer.writerows(data)

    print(f"✅ Data saved to {file_path}")
    write_log(f"✅ Data saved to {file_path}")

def write_log(message):
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_path = f"{LOG_FOLDER}/{today}.log"
    
    with open(log_path, mode='a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def main():
    try:
        print("🚀 Starting MRT data crawler...")
        write_log("🚀 Starting MRT data crawler...")

        data = crawl_data()
        save_to_csv(data)

        print("✅ Finished successfully.")
        write_log("✅ Finished successfully.")

    except Exception as e:
        error_message = f"❌ Error occurred: {str(e)}"
        print(error_message)
        write_log(error_message)
        write_log(traceback.format_exc())

if __name__ == "__main__":
    main()
