import aiosqlite
import os
from datetime import datetime
from typing import Optional


DB_PATH = "data/bot.db"


async def init_db():
    """Инициализация базы данных"""
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 0,
                remnawave_uuid TEXT,
                subscription_end TIMESTAMP,
                referrer_id INTEGER,
                referral_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                amount REAL,
                type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                bonus_rub REAL,
                uses_left INTEGER,
                is_active INTEGER DEFAULT 1
            )
        """)
        await db.commit()


async def get_user(telegram_id: int) -> Optional[dict]:
    """Получить пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_user(telegram_id: int, username: str, referrer_id: Optional[int] = None) -> dict:
    """Создать нового пользователя"""
    import secrets
    referral_code = secrets.token_hex(4).upper()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users 
               (telegram_id, username, referrer_id, referral_code) 
               VALUES (?, ?, ?, ?)""",
            (telegram_id, username, referrer_id, referral_code)
        )
        await db.commit()
        return await get_user(telegram_id)


async def update_balance(telegram_id: int, amount: float, description: str) -> float:
    """Обновить баланс и записать транзакцию"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.execute(
            "INSERT INTO transactions (telegram_id, amount, type, description) VALUES (?, ?, ?, ?)",
            (telegram_id, amount, "topup" if amount > 0 else "purchase", description)
        )
        await db.commit()
        user = await get_user(telegram_id)
        return user["balance"]


async def update_subscription_end(telegram_id: int, end_date: datetime, remnawave_uuid: str):
    """Обновить дату окончания подписки"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET subscription_end = ?, remnawave_uuid = ? WHERE telegram_id = ?",
            (end_date.isoformat(), remnawave_uuid, telegram_id)
        )
        await db.commit()


async def get_expiring_users(days_before: int) -> list:
    """Получить пользователей, у которых подписка истекает через N дней"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM users 
               WHERE subscription_end IS NOT NULL 
               AND date(subscription_end) = date('now', '+' || ? || ' days')""",
            (days_before,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def activate_promo_code(telegram_id: int, code: str) -> Optional[float]:
    """Активировать промокод"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT bonus_rub, uses_left FROM promo_codes WHERE code = ? AND is_active = 1",
            (code.upper(),)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            bonus = row[0]
            uses_left = row[1] - 1
            await db.execute(
                "UPDATE promo_codes SET uses_left = ?, is_active = CASE WHEN ? = 0 THEN 0 ELSE 1 END WHERE code = ?",
                (uses_left, uses_left, code.upper())
            )
            await db.commit()
            await update_balance(telegram_id, bonus, f"Промокод {code}")
            return bonus


async def get_referral_stats(telegram_id: int) -> dict:
    """Получить статистику по рефералам"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id = ?",
            (telegram_id,)
        ) as cursor:
            count = (await cursor.fetchone())[0]
        async with db.execute(
            "SELECT referral_code FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            code = (await cursor.fetchone())[0]
        return {"count": count, "code": code}
