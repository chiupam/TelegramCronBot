# Telegram Cron Bot

基于 Docker 的 Telegram 定时任务机器人，支持通过 YAML 配置文件管理定时消息发送任务。

## 快速开始

### 1. 配置环境变量

复制示例环境变量文件并填写你的 Telegram API 凭证：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+86138xxxxxxxx
LOG_LEVEL=INFO
```

| 变量 | 说明 |
|------|------|
| `TELEGRAM_API_ID` | 从 [my.telegram.org](https://my.telegram.org) 获取 |
| `TELEGRAM_API_HASH` | 从 [my.telegram.org](https://my.telegram.org) 获取 |
| `TELEGRAM_PHONE` | 登录手机号（带国家区号） |
| `LOG_LEVEL` | 日志等级：`DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |

### 2. 构建并启动容器

```bash
docker-compose up -d --build
```

### 3. 登录 Telegram

```bash
docker exec -it bot tglogin
```

执行后：
- 如果 `.env` 中预设了手机号，会自动使用该手机号，只需输入验证码
- 如果未预设手机号，会提示输入手机号，再输入验证码
- 如果开启了两步验证，会提示输入密码

**重新登录：**
```bash
docker exec -it bot rm /app/data/bot.session
docker exec -it bot tglogin
```

登录状态会自动持久化到 `./data/bot.session`，容器重启后无需重新登录。

### 4. 配置定时任务

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

## 常用命令

| 命令 | 说明 |
|------|------|
| `docker-compose up -d --build` | 构建并启动容器 |
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
