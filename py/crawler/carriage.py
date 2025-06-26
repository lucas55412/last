import requests
import csv
from datetime import datetime
import os
import json

# 設定資料夾與日誌路徑
BASE_DIR = "/Users/angelina1114/Desktop/Final_report"
DATA_FOLDER = f"{BASE_DIR}/MRT_carriage_data"
LOG_FOLDER = f"{DATA_FOLDER}/logs"

def crawl_data():
    """主要的爬蟲函數，用於抓取捷運車廂擁擠度資料"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    with open("/Users/angelina1114/Desktop/Final_report/MRT_line.json", encoding="utf-8") as f:
        line_data = json.load(f)
        
    for line in line_data:
        line_info = line_data[line]
        line_name = line_info.get("name")
        line_id = line_info.get("id")

        url = f"https://citydashboard.taipei/api/v1/component/{line_id}/chart?city=taipei"
        print(f"正在處理 {line_name} 的資料 (id: {line_id})")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            api_data = response.json()
            write_log(f"✅ {line_name} 的資料成功獲取")

        except requests.RequestException as e:
            write_log(f"❌ {line_name} 的資料獲取失敗（requests: {e}")
            continue

        # 特別處理 Orange 分支
        try:
            if line == "Orange":
                station_data = line_info["station"]
                common = station_data.get("共同", {})
                to_hl = station_data.get("to迴龍", {})
                to_lz = station_data.get("to蘆洲", {})

                com = merge_data(api_data, common)
                hl = merge_data(api_data, to_hl)
                lz = merge_data(api_data, to_lz)

                results = (
                    com +
                    [["---往迴龍---", "", "", ""]] +
                    hl +
                    [["---往蘆洲---", "", "", ""]] +
                    lz
                )
            else:
                station_dict = line_info["station"]
                results = merge_data(api_data, station_dict)

            save_to_csv(line_info, line_name, results)
        except Exception as e:
            write_log(f"❌ {line_name} 處理失敗（非 requests）: {e}")

def merge_data(api_data, station_dict):
    """合併 API 資料與站點資訊"""
    merged = {code: [name, "----", "----"] for code, name in station_dict.items()}

    for point in api_data["data"][0]["data"]:
        raw_code = point["x"]
        if len(raw_code) < 3:
            write_log(f"⚠️ 發現無效 raw_code: '{raw_code}'，已跳過")
            continue
        direction = raw_code[0]
        station_code = raw_code[1:]
        crowding_degree = point["y"]

        if station_code not in merged:
            continue  # 忽略不是這段的站

        if direction == "A":
            merged[station_code][1] = crowding_degree
        elif direction == "D":
            merged[station_code][2] = crowding_degree

    # 排序並轉換為 list
    sorted_results = sorted(merged.items(), key=lambda x: x[0])
    results = [[code, name, to_a, to_d] for code, (name, to_a, to_d) in sorted_results]
    return results

def save_to_csv(line_info, line_name, results):
    """將資料儲存為 CSV 檔案"""
    station_data = line_info.get("station")
    if isinstance(station_data, dict) and all(isinstance(v, str) for v in station_data.values()):
        last_name = list(station_data.values())[-1]
        first_name = list(station_data.values())[0]
    else:
        first_name = "南勢角"
        last_name = "蘆洲迴龍"

    now = datetime.now().strftime("%H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")

    LINE_FOLDER = os.path.join(DATA_FOLDER, line_name)
    os.makedirs(LINE_FOLDER, exist_ok=True)

    file_path = f"{LINE_FOLDER}/{today}-{weekday}.csv"
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([f"=={now}==", "", "", ""])
        
        if os.path.getsize(file_path) == 0:
            # 如果檔案是空的，寫入標題
            writer.writerow(["編號", "站名", f"往{last_name}", f"往{first_name}"])
        writer.writerows(results)
        print(f"✅ Data saved to {file_path}")
        write_log(f"✅ Data saved to {file_path}")

def write_log(message):
    """寫入日誌檔案"""
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_path = f"{LOG_FOLDER}/{today}.log"
    
    with open(log_path, mode='a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

crawl_data()
