import asyncio
import os
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = int(os.environ.get("TELEGRAM_API_ID", "0"))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
PHONE = os.environ.get("TELEGRAM_PHONE", "")
SESSION_PATH = os.environ.get("SESSION_PATH", "/app/data/bot.session")

async def main():
    if not API_ID or not API_HASH:
        print("错误：请设置环境变量 TELEGRAM_API_ID 和 TELEGRAM_API_HASH")
        sys.exit(1)

    session_file = Path(SESSION_PATH)
    if session_file.exists():
        print("检测到已存在登录会话文件 (bot.session)。")
        print("如需重新登录，请先删除该文件：")
        print(f"  docker exec -it bot rm {SESSION_PATH}")
        print("然后再次执行 tglogin。")
        return

    print("未检测到登录会话，开始登录流程...\n")

    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

    try:
        if PHONE:
            print(f"使用预设手机号: {PHONE}")
            await client.start(phone=PHONE)
        else:
            print("未预设手机号，请按提示输入。")
            await client.start()
    except SessionPasswordNeededError:
        password = input("请输入两步验证密码: ")
        if PHONE:
            await client.start(phone=PHONE, password=password)
        else:
            await client.start(password=password)

    if await client.is_user_authorized():
        print("\n登录成功！")
        me = await client.get_me()
        print(f"当前用户: {me.first_name} (@{me.username})")
        print(f"会话已保存至: {SESSION_PATH}")
    else:
        print("\n登录失败，请检查验证码。")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
