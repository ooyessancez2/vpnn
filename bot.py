import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    bot_token = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    if bot_token == "YOUR_BOT_TOKEN_HERE":
        logging.warning("BOT_TOKEN не задан в .env! Бот работает в режиме ожидания.")
    
    logging.info("========================================")
    logging.info("  CYBER VPN BOT INITIALIZED SUCCESSFULLY")
    logging.info("  Status: Waiting for real bot code...")
    logging.info("========================================")
    
    # Держим контейнер живым
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
