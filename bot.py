import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from croniter import croniter
from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
level = level_map.get(LOG_LEVEL, logging.DEBUG)

logging.basicConfig(
    level=level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/app/data/bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

def get_env_int(name, default=0):
    val = os.environ.get(name, str(default))
    try:
        return int(val)
    except ValueError:
        return default

API_ID = get_env_int("TELEGRAM_API_ID", 0)
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
SESSION_PATH = os.environ.get("SESSION_PATH", "/app/data/bot.session")
CONFIG_DIR = os.environ.get("CONFIG_DIR", "/app/data")

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

tasks = []
scheduled_jobs = []

async def load_config():
    global tasks
    config_path = Path(CONFIG_DIR)
    logger.debug(f"开始扫描配置目录: {config_path}")

    new_tasks = []
    if not config_path.exists():
        logger.warning(f"配置目录不存在: {config_path}")
        return new_tasks

    for yaml_file in sorted(config_path.glob("*.yaml")):
        logger.debug(f"发现配置文件: {yaml_file}")
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                logger.warning(f"配置文件为空: {yaml_file}")
                continue
            file_tasks = data if isinstance(data, list) else [data]
            for task in file_tasks:
                if all(k in task for k in ("cron", "target", "command")):
                    new_tasks.append(task)
                    logger.debug(f"加载任务: cron={task['cron']}, target={task['target']}, command={task['command']}")
                else:
                    logger.warning(f"任务字段不完整，已跳过: {task}")
            logger.info(f"配置文件解析成功: {yaml_file}, 任务数: {len(file_tasks)}")
        except Exception as e:
            logger.error(f"解析配置文件失败 {yaml_file}: {e}", exc_info=True)

    tasks = new_tasks
    logger.info(f"配置加载完成，当前总任务数: {len(tasks)}")
    return tasks

def schedule_tasks():
    global scheduled_jobs
    scheduled_jobs.clear()
    logger.debug("清空现有定时任务，准备重新调度")

    for idx, task in enumerate(tasks):
        try:
            itr = croniter(task["cron"], datetime.now())
            next_run = itr.get_next(datetime)
            scheduled_jobs.append({
                "id": idx,
                "cron": task["cron"],
                "target": task["target"],
                "command": task["command"],
                "next_run": next_run,
                "iter": itr,
            })
            logger.debug(f"任务已调度: id={idx}, next_run={next_run}, target={task['target']}, command={task['command']}")
        except Exception as e:
            logger.error(f"调度任务失败 (cron={task['cron']}): {e}", exc_info=True)

    logger.info(f"定时任务调度完成，共 {len(scheduled_jobs)} 个任务")

async def send_message(target, command):
    try:
        logger.debug(f"准备发送消息: target={target}, command={command}")
        entity = await client.get_entity(target)
        await client.send_message(entity, command)
        logger.info(f"消息发送成功: target={target}, command={command}")
        return True
    except FloodWaitError as e:
        logger.warning(f"触发 FloodWait，需等待 {e.seconds} 秒: target={target}")
        return False
    except RPCError as e:
        logger.error(f"Telegram API 错误: {e}, target={target}, command={command}")
        return False
    except Exception as e:
        logger.error(f"发送消息异常: {e}, target={target}, command={command}", exc_info=True)
        return False

async def run_scheduler():
    while True:
        now = datetime.now()
        for job in scheduled_jobs:
            if job["next_run"] <= now:
                logger.debug(f"任务触发: id={job['id']}, target={job['target']}, command={job['command']}")
                await send_message(job["target"], job["command"])
                job["next_run"] = job["iter"].get_next(datetime)
                logger.debug(f"任务下次执行时间更新: id={job['id']}, next_run={job['next_run']}")
        await asyncio.sleep(1)

async def watch_config():
    config_path = Path(CONFIG_DIR)
    last_mtime = {}
    first_scan = True
    while True:
        try:
            changed = False
            for yaml_file in sorted(config_path.glob("*.yaml")):
                mtime = yaml_file.stat().st_mtime
                if yaml_file not in last_mtime:
                    last_mtime[yaml_file] = mtime
                    if not first_scan:
                        changed = True
                elif last_mtime[yaml_file] != mtime:
                    last_mtime[yaml_file] = mtime
                    changed = True
            if changed:
                logger.info("检测到配置文件变更，重新加载...")
                await load_config()
                schedule_tasks()
            first_scan = False
        except Exception as e:
            logger.error(f"监控配置文件异常: {e}", exc_info=True)
        await asyncio.sleep(5)

async def main():
    logger.info("应用启动")
    if not API_ID or not API_HASH:
        logger.error("缺少环境变量 TELEGRAM_API_ID 或 TELEGRAM_API_HASH")
        sys.exit(1)

    logger.debug(f"SESSION_PATH={SESSION_PATH}, CONFIG_DIR={CONFIG_DIR}")
    await client.start()
    if not await client.is_user_authorized():
        logger.error("用户未登录，请先执行 docker exec -it bot tglogin")
        sys.exit(1)
    me = await client.get_me()
    logger.info(f"Telegram 客户端已连接，用户: {me.first_name} (@{me.username})")

    await load_config()
    schedule_tasks()

    # 启动后给 @me 发送运行状态消息
    try:
        startup_msg = (
            f"🤖 <b>Telegram Cron Bot 已启动</b>\n"
            f"\n"
            f"👤 用户: {me.first_name} (@{me.username})\n"
            f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📋 任务数: {len(tasks)}\n"
            f"\n"
            f"✅ 系统运行正常"
        )
        await client.send_message(me, startup_msg, parse_mode="html")
        logger.info("启动通知已发送至 @me")
    except Exception as e:
        logger.warning(f"发送启动通知失败: {e}")

    await asyncio.gather(
        run_scheduler(),
        watch_config(),
    )

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("应用收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"应用异常退出: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("应用已停止")
