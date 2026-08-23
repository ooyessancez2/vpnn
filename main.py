import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from database import init_db
from scheduler import setup_scheduler

# Импортируем роутеры
from handlers import start, subscription, balance, referral, promo

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("========================================")
    logger.info("  CYBER VPN BOT - ЗАПУСК СИСТЕМЫ")
    logger.info("========================================")
    
    # Инициализация базы данных
    await init_db()
    logger.info("✓ База данных инициализирована")
    
    # Создание бота и диспетчера
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение роутеров
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(balance.router)
    dp.include_router(referral.router)
    dp.include_router(promo.router)
    
    # Настройка планировщика уведомлений
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("✓ Планировщик уведомлений запущен")
    
    # Запуск бота
    logger.info("✓ Бот запущен и готов к работе")
    logger.info("========================================")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
