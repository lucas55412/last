# Gunicorn 配置文件

# 綁定的 IP 和端口
bind = "0.0.0.0:8000"

# 工作進程數
workers = 4

# 工作模式
worker_class = "sync"

# 每個工作進程的最大請求數
max_requests = 1000
max_requests_jitter = 50

# 超時設置（秒）
timeout = 30
keepalive = 2

# 日誌設置
accesslog = "-"  # 標準輸出
errorlog = "-"   # 標準輸出
loglevel = "info"

# 進程名稱
proc_name = "flask_app"

# 是否後台運行
daemon = False

# 是否重載
reload = True

# 優雅的重啟/關閉時間（秒）
graceful_timeout = 30 