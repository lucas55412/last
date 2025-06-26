#!/usr/bin/env python3
import os
import signal
import sys
import psutil
import time

def find_and_kill_flask():
    """找到並終止所有 Flask 相關的進程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 檢查是否是 Python 進程
            if proc.info['name'] == 'Python' or proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                cmdline = proc.info['cmdline']
                if cmdline and ('flask' in ' '.join(cmdline).lower() or 'app.py' in ' '.join(cmdline)):
                    print(f"終止 Flask 進程: {proc.info['pid']}")
                    proc.terminate()
                    proc.wait(timeout=3)  # 等待進程終止
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            continue

def cleanup(signum, frame):
    """清理函數，確保程式正常退出"""
    print("\n正在清理並退出...")
    find_and_kill_flask()
    sys.exit(0)

def main():
    """主函數，運行 Flask 應用"""
    # 先清理可能存在的殘留進程
    find_and_kill_flask()
    
    # 設置信號處理
    signal.signal(signal.SIGINT, cleanup)   # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # 終止信號
    
    # 運行 Flask 應用
    port = int(os.environ.get('PORT', 8080))
    os.system(f'python app.py')

if __name__ == '__main__':
    main() 