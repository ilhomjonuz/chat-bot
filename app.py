import asyncio
import logging
import sys

from loader import dp, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

async def on_startup():
    await set_default_commands()
    await on_startup_notify()

async def main():
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("❌ Bot to‘xtatildi!")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🚀 Dastur to‘xtatildi!")
