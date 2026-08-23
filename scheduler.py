from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database import get_expiring_users
from texts import NOTIFY_3_DAYS, NOTIFY_24_HOURS
from config import settings


async def send_3_days_notification(bot: Bot):
    """Уведомление за 3 дня до окончания"""
    if not settings.notify_3_days_before:
        return
    
    users = await get_expiring_users(3)
    for user in users:
        try:
            await bot.send_message(
                user["telegram_id"],
                NOTIFY_3_DAYS,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending 3-day notification to {user['telegram_id']}: {e}")


async def send_24_hours_notification(bot: Bot):
    """Уведомление за 24 часа до окончания"""
    if not settings.notify_24_hours_before:
        return
    
    users = await get_expiring_users(1)
    for user in users:
        try:
            await bot.send_message(
                user["telegram_id"],
                NOTIFY_24_HOURS,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending 24h notification to {user['telegram_id']}: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Настройка планировщика"""
    scheduler = AsyncIOScheduler()
    
    # Проверка каждый час в 10:00
    scheduler.add_job(
        send_3_days_notification,
        'cron',
        hour=10,
        args=[bot]
    )
    
    scheduler.add_job(
        send_24_hours_notification,
        'cron',
        hour=10,
        args=[bot]
    )
    
    return scheduler
