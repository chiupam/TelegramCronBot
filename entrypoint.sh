#!/bin/bash
set -e

CONFIG_DIR="${CONFIG_DIR:-/app/data}"

if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

if [ ! -f "$CONFIG_DIR/tasks.yaml" ]; then
    echo "未检测到 tasks.yaml，生成默认配置文件..."
    cat > "$CONFIG_DIR/tasks.yaml" << 'EOF'
- cron: "0 9 * * *"
  target: "@me"
  command: "早安，今天是新的一天！"
EOF
    echo "默认配置已生成: $CONFIG_DIR/tasks.yaml"
fi

if [ "$1" = "tglogin" ]; then
    exec python /app/login.py
fi

exec "$@"
