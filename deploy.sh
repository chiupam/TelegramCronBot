#!/bin/bash
set -e

REPO="chiupam/tgbot"
COMPOSE_URL="https://raw.githubusercontent.com/chiupam/TelegramCronBot/main/docker-compose.yml"

echo "========================================"
echo "  Telegram Cron Bot 一键部署脚本"
echo "========================================"
echo ""

if ! command -v docker &> /dev/null; then
    echo "错误：未检测到 Docker，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误：未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

if [ -f "docker-compose.yml" ]; then
    echo "检测到当前目录已存在 docker-compose.yml"
    read -p "是否覆盖并重新配置? [y/N]: " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "已取消部署"
        exit 0
    fi
    echo ""
fi

echo "请配置 Telegram API 凭证（从 https://my.telegram.org 获取）"
echo ""

while true; do
    read -p "TELEGRAM_API_ID: " api_id
    if [[ "$api_id" =~ ^[0-9]+$ ]]; then
        break
    fi
    echo "错误：API_ID 必须是数字，请重新输入"
done

while true; do
    read -p "TELEGRAM_API_HASH: " api_hash
    if [ -n "$api_hash" ]; then
        break
    fi
    echo "错误：API_HASH 不能为空，请重新输入"
done

read -p "TELEGRAM_PHONE (带国家区号，如 +86138xxxxxxxx，回车跳过): " phone

echo ""
echo "请选择日志等级:"
echo "  1) DEBUG - 调试信息最详细"
echo "  2) INFO  - 一般信息（推荐）"
echo "  3) WARNING - 只显示警告和错误"
echo "  4) ERROR - 只显示错误"
echo "  5) CRITICAL - 只显示严重错误"

while true; do
    read -p "输入数字 [1-5，默认2]: " log_choice
    log_choice=${log_choice:-2}
    case "$log_choice" in
        1) log_level="DEBUG"; break ;;
        2) log_level="INFO"; break ;;
        3) log_level="WARNING"; break ;;
        4) log_level="ERROR"; break ;;
        5) log_level="CRITICAL"; break ;;
        *) echo "无效选择，请重新输入" ;;
    esac
done

echo ""
echo "正在下载 docker-compose.yml..."

if command -v curl &> /dev/null; then
    curl -fsSL -o docker-compose.yml "$COMPOSE_URL"
elif command -v wget &> /dev/null; then
    wget -q -O docker-compose.yml "$COMPOSE_URL"
else
    echo "错误：需要 curl 或 wget 来下载文件"
    exit 1
fi

sed -i.bak \
    -e "s/TELEGRAM_API_ID=12345678/TELEGRAM_API_ID=$api_id/" \
    -e "s/TELEGRAM_API_HASH=your_api_hash/TELEGRAM_API_HASH=$api_hash/" \
    -e "s/TELEGRAM_PHONE=+86138xxxxxxxx/TELEGRAM_PHONE=${phone:-}/" \
    -e "s/LOG_LEVEL=INFO/LOG_LEVEL=$log_level/" \
    docker-compose.yml

rm -f docker-compose.yml.bak

echo ""
echo "========================================"
echo "  配置完成！"
echo "========================================"
echo ""
echo "TELEGRAM_API_ID: $api_id"
echo "TELEGRAM_API_HASH: ${api_hash:0:4}****"
echo "TELEGRAM_PHONE: ${phone:-未设置}"
echo "LOG_LEVEL: $log_level"
echo ""
echo "正在启动容器..."
echo ""

if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo ""
echo "========================================"
echo "  部署成功！"
echo "========================================"
echo ""
echo "下一步：登录 Telegram"
echo "  docker exec -it bot tglogin"
echo ""
echo "查看日志："
echo "  docker logs -f bot"
echo ""
echo "编辑定时任务："
echo "  ./data/tasks.yaml"
echo ""
