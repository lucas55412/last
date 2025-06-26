# Flask 部落格與捷運資訊系統
## 期末專題報告

### 動機

我希望透過整合社交平台與台北捷運即時資訊的網站開發，實作一個具備資料互動與視覺化功能的全端系統，強化自己在後端資料處理、前端顯示與 API 整合等能力。
且因為每天上學通勤工具是捷運，所以希望透過他重並是覺話可以更熟知離、尖峰時段


### 核心功能和成果展示

### 使用說明
#### 基本功能操作

1. **註冊新帳號**
   - 訪問首頁，點擊「註冊」
   - 填寫用戶名、電子郵件和密碼
   - 系統會驗證資料唯一性

2. **發表文章**
   - 登入後點擊「發表文章」
   - 輸入標題和內容
   - 發布後可在首頁查看

3. **互動功能**
   - 點擊文章標題查看詳情
   - 在文章頁面留言
   - 查看其他用戶的個人頁面

4. **捷運資訊查看**
   - 點擊導航欄「捷運資訊」
   - 查看即時車廂擁擠度
   - 瀏覽人流統計圖表

### 系統架構

```
├── app.py                 # 主應用程式檔案
├── init_yeeeeeeeeee.py、init.py ＃新增資料庫表格（只需跑一次） 
├── 1.txt.                       ＃讓後端程式可以透過帳號密碼，在他的後端連接資料庫
├── templates/           # HTML 模板目錄 
│   ├── base.html        # 基礎模板 
│   ├── index.html       # 首頁模板 
│   ├── login.html       # 登入頁面 
│   ├── register.html    # 註冊頁面 
│   ├── create_post.html # 發文頁面 
│   ├── view_post.html   # 文章詳情頁面 
│   └── mrt_dashboard.html # 捷運資訊儀表板 
├── static/    # 靜態資源目錄 
│   ├── css/            # 樣式檔案 
└── crawler/            # 資料爬蟲模組
```

### 資料庫設計

###用docker建立資料庫或是讓讓docker跑起來拿到資料庫的東西

＃創建新資料夾：docker run -e "ACCEPT_EULA=Y" \
  -e 'SA_PASSWORD=YourStrong!Passw0rd' \-p 1433:1433 
  \ -v sqlserverdata:/var/opt/mssql \
  --name sqlserver \
  -d mcr.microsoft.com/mssql/server:2022-latest
\*除非刪掉否則只執行一次*\

＃重新啟動docker資料夾docker start sqlserver


#### Collections (集合)

1. **users** - 用戶資料
   ```javascript
   {
     _id: ObjectId,
     username: String,
     email: String,
     password_hash: String,
     created_at: DateTime
   }
   ```

2. **posts** - 文章資料
   ```javascript
   {
     _id: ObjectId,
     title: String,
     content: String,
     user_id: ObjectId,
     created_at: DateTime
   }
   ```

3. **comments** - 留言資料
   ```javascript
   {
     _id: ObjectId,
     content: String,
     post_id: ObjectId,
     user_id: ObjectId,
     created_at: DateTime
   }
   ```

4. **mrt_carriage** - 捷運車廂資料
   ```javascript
   {
     _id: ObjectId,
     line_code: String,
     line_name: String,
     station_code: String,
     station_name: String,
     to_terminal: Array,
     to_start: Array,
     timestamp: DateTime
   }
   ```

5. **mrt_stream** - 捷運人流資料
   ```javascript
   {
     _id: ObjectId,
     count: Number,
     timestamp: DateTime,
     date: String,
     time: String,
     weekday: String
   }
   ```

### API 端點

#### REST API 路由

| HTTP Method | 端點 | 說明 |
|-------------|------|------|
| GET | `/` | 首頁 - 顯示所有文章 |
| GET/POST | `/login` | 用戶登入 |
| GET/POST | `/register` | 用戶註冊 |
| GET | `/logout` | 用戶登出 |
| GET/POST | `/post/create` | 創建文章 |
| GET | `/post/<post_id>` | 查看文章詳情 |
| POST | `/post/<post_id>/comment` | 添加留言 |
| GET | `/user/<username>` | 用戶個人頁面 |
| GET | `/mrt` | 捷運資訊儀表板 |

#### JSON API 端點

| 端點 | 說明 | 回傳格式 |
|------|------|----------|
| `/api/mrt/carriage/<line_name>` | 車廂擁擠度資料 | JSON Array |
| `/api/mrt/stream` | 人流統計資料 | JSON Array |

### 安裝與部署指南

#### 本地開發環境

1.**建立虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

2. **環境變數設定**
   建立 `1.txt` 檔案 (可選，本專案已內建預設值) 

DB_SERVER=localhost,1433
DB_USER=sa
DB_PASSWORD=YourStrong!Passw0rd
DB_NAME=master

3. **啟動應用程式**
   ```bash
   python app.py
   ```



### 未來擴展方向

1. **功能擴展**
   - 圖片上傳功能
   - 文章分類系統
   - 私訊功能
   - 通知系統

2. **技術優化**
   - 快取機制實現
   - 資料庫查詢優化
   - 前端框架升級 (React/Vue)

3. **資料分析**
   - 用戶行為分析
   - 交通模式預測
   - 個人化推薦系統

### 專案資訊

- **開發者**: [許順傑]
- **學號**: [413170202]
- **課程**: [程式設計2]
- **指導教授**: [潘俊傑]
- **開發時間**: [6/10]
- **專案版本**: v1.0.0

---

*此專案為學術用途開發，展示 Flask Web 開發技術與資料視覺化應用整合能力。* 
