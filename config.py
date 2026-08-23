from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация из .env — секреты только здесь, в коде их нет."""

    # ===== TELEGRAM =====
    bot_token: str
    admin_ids: List[int] = []

    # ===== REMNAWAVE =====
    remnawave_api_url: str = "https://panel.example.com"
    remnawave_api_key: str = ""

    # ===== CRYPTOBOT =====
    cryptobot_api_token: str = ""
    cryptobot_network: str = "mainnet"

    # ===== ЦЕНЫ (руб) =====
    price_30_days: int = 100
    price_90_days: int = 270
    price_180_days: int = 500

    # ===== УВЕДОМЛЕНИЯ =====
    notify_3_days_before: bool = True
    notify_24_hours_before: bool = True

    # ===== DATABASE =====
    database_url: str = "sqlite+aiosqlite:///./data/bot.db"

    # ===== REFERRAL =====
    referral_bonus_rub: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   # лишние переменные из .env (POSTGRES_* и т.д.) не ломают старт
    )


settings = Settings()
