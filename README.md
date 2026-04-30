# Telegram Cron Bot

基于 Docker 的 Telegram 定时任务机器人，支持通过 YAML 配置文件或 Telegram 消息管理定时消息发送任务。

## 快速开始

### 一键部署（推荐）

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/chiupam/TelegramCronBot/main/deploy.sh)
```

执行后按提示输入：
- `TELEGRAM_API_ID` 和 `TELEGRAM_API_HASH`（从 [my.telegram.org](https://my.telegram.org) 获取）
- `TELEGRAM_PHONE`（带国家区号的手机号，可选）
- 日志等级（默认 INFO）

脚本会自动下载 `docker-compose.yml`、填充配置并启动容器。

### 手动部署

如果你不想使用一键脚本，也可以手动配置：

#### 1. 创建 docker-compose.yml

```yaml
services:
  bot:
    image: chiupam/tgbot:latest
    container_name: bot
    environment:
      - TELEGRAM_API_ID=你的_api_id
      - TELEGRAM_API_HASH=你的_api_hash
      - TELEGRAM_PHONE=+86138xxxxxxxx
      - SESSION_PATH=/app/data/bot.session
      - CONFIG_DIR=/app/data
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    stdin_open: true
    tty: true
```

#### 2. 启动容器

```bash
docker-compose up -d
```

首次启动时，如果 `./data/tasks.yaml` 不存在，会自动生成一份默认配置。

### 登录 Telegram

```bash
docker exec -it bot tglogin
```

执行后：
- 如果 `docker-compose.yml` 中预设了手机号，会自动使用该手机号，只需输入验证码
- 如果未预设手机号，会提示输入手机号，再输入验证码
- 如果开启了两步验证，会提示输入密码

**重新登录：**
```bash
docker exec -it bot rm /app/data/bot.session
docker exec -it bot tglogin
```

登录状态会自动持久化到 `./data/bot.session`，容器重启后无需重新登录。

## 配置定时任务

### 方式一：Telegram 消息命令（推荐）

向自己的 **Saved Messages（@me）**发送以下命令：

| Command | Description | Example |
|---------|-------------|---------|
| `status` | View task list and next execution time | `status` |
| `add` | Add scheduled task | `add 0 9 * * *\|@me\|Good morning` |
| `del` | Delete task by ID | `del 0` |
| `help` | Show help | `help` |

**Add task format:**
```
add cron|target|content
```

注意：分隔符是 `|`（竖线），如果内容里有 `|` 会被截断。

### 方式二：编辑配置文件

编辑 `./data/tasks.yaml` 文件添加或修改定时任务，配置变更会自动生效。

示例配置：

```yaml
- cron: "0 9 * * *"
  target: "@testbot"
  command: "/start"

- cron: "0 20 * * *"
  target: "@testbot"
  command: "/stop"
```

## 配置文件说明

| 字段 | 说明 |
|------|------|
| `cron` | crontab 表达式（容器使用北京时间 CST） |
| `target` | 目标用户或群组（用户名/ID） |
| `command` | 要发送的指令内容 |

## 告警通知

当定时消息发送失败时，Bot 会自动向你的 **Saved Messages（@me）**发送告警，包含：
- 失败原因（FloodWait / API 错误 / 异常）
- 目标用户
- 消息内容

## 常用命令

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 启动容器 |
| `docker exec -it bot tglogin` | 启动 Telegram 登录 |
| `docker logs -f bot` | 查看实时日志 |
| `docker-compose down` | 停止容器 |
| `docker-compose restart` | 重启容器 |

## 持久化数据

所有数据统一存放在 `./data` 目录：

| 文件 | 说明 |
|------|------|
| `./data/bot.session` | Telegram 登录会话文件 |
| `./data/tasks.yaml` | YAML 配置文件 |
| `./data/bot.log` | 应用日志文件 |

## 时区

容器内时区设置为 **Asia/Shanghai（北京时间）**，crontab 表达式按照北京时间执行。
