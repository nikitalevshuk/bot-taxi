import asyncio
import logging
import os
from datetime import datetime, time
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from sqlalchemy import select

from bot.database import AsyncSessionLocal, engine
from bot.handlers import router
from bot.middlewares import DatabaseMiddleware
from bot.models import Base, User, WorkSchedule
from bot.charts import generate_work_hours_histogram

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)

# Admin user ID
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

async def on_startup():
    # Drop and recreate database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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

async def send_admin_reports():
    """Send work hours reports to admin at specified times"""
    report_hours = {8, 15, 21, 24}
    while True:
        try:
            tz = pytz.timezone('Europe/Warsaw')
            now = datetime.now(tz)
            
            if now.hour in report_hours and now.minute == 0:
                async with AsyncSessionLocal() as session:
                    # Get all cities
                    cities = await session.execute(
                        select(User.city).distinct()
                    )
                    cities = [city[0] for city in cities.all()]
                    
                    # Generate and send report for each city
                    for city in cities:
                        try:
                            # Generate histogram
                            histogram_buf = await generate_work_hours_histogram(session, city)
                            
                            # Send report to admin
                            await bot.send_photo(
                                chat_id=ADMIN_USER_ID,
                                photo=FSInputFile(histogram_buf, filename=f"{city}_report.png"),
                                caption=f"Work hours report for {city} at {now.strftime('%H:00')}"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send report for {city}: {e}")
            
            # Wait for the next minute
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in admin report loop: {e}")
            await asyncio.sleep(60)

async def main():
    # Initialize dispatcher
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(router)
    
    # Setup middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    # Start background tasks
    asyncio.create_task(notify_users_daily())
    asyncio.create_task(send_admin_reports())
    
    # Start polling
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
