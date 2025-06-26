# Flask 部落格與捷運資訊系統
## 期末專題報告

### 動機

我希望透過整合社交平台與台北捷運即時資訊的網站開發，實作一個具備資料互動與視覺化功能的全端系統，強化自己在後端資料處理、前端顯示與 API 整合等能力。
且因為每天上學通勤工具是捷運，所以希望透過他重並是覺話可以更熟知離、尖峰時段


### 核心功能和成果展示

#### 1. 用戶管理系統
- **用戶註冊與登入**
- **會話管理**: Flask-Session 實現用戶狀態管理
- **個人資料頁面**: 顯示用戶發表的所有文章

#### 2. 部落格系統
- **文章發布**: 支援標題和內容編輯
- **文章瀏覽**: 按時間排序的文章列表
- **留言功能**: 用戶可對文章進行評論互動

#### 3. 捷運資訊視覺化
- **即時車廂擁擠度**: 顯示各路線車廂的擁擠狀況
- **人流統計圖表**: 以圖表形式展示各時段的人流變化
- **多路線支援**: 支援台北捷運多條路線的資料展示

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

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd final-project
   ```

2. **建立虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **環境變數設定**
   建立 `.env` 檔案 (可選，本專案已內建預設值)
   ```
   MONGODB_URI=your_mongodb_connection_string
   SECRET_KEY=your_secret_key
   FLASK_DEBUG=True
   ```

5. **啟動應用程式**
   ```bash
   python app.py
   ```
   
   應用程式將在 http://localhost:8080 啟動

#### 雲端部署 (Render)

本專案已配置在 Render 平台自動部署：

1. **部署 URL**: https://final-project-o69j.onrender.com
2. **自動部署**: 推送到 main 分支時自動觸發部署
3. **環境變數**: 已在 Render 控制台配置

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

### 技術特色與創新點

#### 1. 模組化架構設計
- 採用 MVC 架構模式
- 資料模型與業務邏輯分離
- 可擴展性強的代碼結構

#### 2. 資料視覺化整合
- 整合即時交通資訊
- 互動式圖表展示
- 多維度資料分析

#### 3. 安全性考量
- 密碼雜湊加密存儲
- 會話管理機制
- SQL 注入防護 (NoSQL)

#### 4. 響應式設計
- Bootstrap 5 響應式框架
- 多裝置兼容性
- 現代化 UI/UX 設計

### 開發挑戰與解決方案

#### 1. 資料庫連接問題
**挑戰**: PyMongo Collection 布林值測試問題
**解決**: 使用明確的 `None` 比較替代布林值測試

#### 2. 模組導入問題
**挑戰**: 生產環境模組路徑錯誤
**解決**: 重構配置管理，將設定整合到主應用檔案

#### 3. 部署配置
**挑戰**: 本地與生產環境配置差異
**解決**: 環境變數動態配置，支援多環境部署

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

### 參考資料

- Flask 官方文檔: https://flask.palletsprojects.com/
- MongoDB 官方文檔: https://docs.mongodb.com/
- Bootstrap 5 文檔: https://getbootstrap.com/docs/5.0/
- Render 部署指南: https://render.com/docs

### 專案資訊

- **開發者**: [簡偉恆、許順傑、盧詠涵]
- **學號**: [413170343,413170202,413170408]
- **課程**: [程式設計2]
- **指導教授**: [潘俊傑]
- **開發時間**: [6/10]
- **專案版本**: v1.0.0

---

*此專案為學術用途開發，展示 Flask Web 開發技術與資料視覺化應用整合能力。* 
