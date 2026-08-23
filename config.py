from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Telegram
    bot_token: str = Field(..., env="BOT_TOKEN")
    admin_ids: List[int] = Field(default=[], env="ADMIN_IDS")
    
    # Remnawave
    remnawave_api_url: str = Field(..., env="REMNAWAVE_API_URL")
    remnawave_api_key: str = Field(..., env="REMNAWAVE_API_KEY")
    
    # CryptoBot
    cryptobot_api_token: str = Field(default="", env="CRYPTOBOT_API_TOKEN")
    cryptobot_network: str = Field(default="mainnet", env="CRYPTOBOT_NETWORK")
    
    # Prices
    price_30_days: int = Field(default=100, env="PRICE_30_DAYS")
    price_90_days: int = Field(default=270, env="PRICE_90_DAYS")
    price_180_days: int = Field(default=500, env="PRICE_180_DAYS")
    
    # Notifications
    notify_3_days_before: bool = Field(default=True, env="NOTIFY_3_DAYS_BEFORE")
    notify_24_hours_before: bool = Field(default=True, env="NOTIFY_24_HOURS_BEFORE")
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/bot.db", env="DATABASE_URL")
    
    # Referral
    referral_bonus_rub: int = Field(default=50, env="REFERRAL_BONUS_RUB")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
