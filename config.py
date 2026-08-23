from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация из .env — секреты только здесь, в коде их нет."""

    # ===== TELEGRAM =====
    bot_token: str
    admin_ids: Union[List[int], int] = []

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

    @field_validator("admin_ids", mode="before")
    @classmethod
    def normalize_admin_ids(cls, v):
        """Принимает: число, список, строку, JSON-строку — приводит к списку int."""
        if v is None or v == "" or v == []:
            return []
        # если уже список
        if isinstance(v, list):
            return [int(x) for x in v if str(x).strip()]
        # если одно число
        if isinstance(v, int):
            return [v]
        # если строка "123" или "123,456" или "[123, 456]"
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            # убираем скобки
            v = v.strip("[]")
            # разбиваем по запятым
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return [int(p) for p in parts]
        return []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
