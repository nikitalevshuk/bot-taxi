import asyncio
import logging
import os
from datetime import datetime, time
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from sqlalchemy import select

from bot.database import AsyncSessionLocal, engine
from bot.handlers import router
from bot.models import Base, User, WorkSchedule

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def notify_users_daily():
    """Notify users at midnight their local time"""
    while True:
        try:
            tz = pytz.timezone('Europe/Warsaw')
            now = datetime.now(tz)
            
            # If it's midnight
            if now.hour == 0 and now.minute == 0:
                async with AsyncSessionLocal() as session:
                    # Get all users
                    users = await session.execute(select(User))
                    for user in users.scalars():
                        try:
                            await bot.send_message(
                                user.telegram_id,
                                "It's a new day! You can now enter your work schedule."
                            )
                        except Exception as e:
                            logger.error(f"Failed to notify user {user.telegram_id}: {e}")
            
            # Wait for the next minute
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in notification loop: {e}")
            await asyncio.sleep(60)

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(router)
    
    # Start notification task
    asyncio.create_task(notify_users_daily())
    
    # Start polling
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
