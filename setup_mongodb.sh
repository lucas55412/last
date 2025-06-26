#!/bin/bash

# 檢查 MongoDB 配置文件位置
if [ -f "/usr/local/etc/mongod.conf" ]; then
    MONGO_CONF="/usr/local/etc/mongod.conf"
elif [ -f "/etc/mongod.conf" ]; then
    MONGO_CONF="/etc/mongod.conf"
else
    echo "找不到 MongoDB 配置文件"
    exit 1
fi

# 備份原始配置文件
cp $MONGO_CONF "${MONGO_CONF}.backup"

# 修改配置文件
cat > $MONGO_CONF << EOL
systemLog:
  destination: file
  path: /usr/local/var/log/mongodb/mongo.log
  logAppend: true
storage:
  dbPath: /usr/local/var/mongodb
net:
  bindIp: 0.0.0.0
  port: 27017
EOL

# 重啟 MongoDB 服務
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    brew services restart mongodb-community
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    sudo systemctl restart mongod
fi

echo "MongoDB 已設置完成，現在允許遠端連接"
echo "請確保防火牆允許 27017 端口的訪問" 