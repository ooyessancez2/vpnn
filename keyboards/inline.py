from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import settings


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ ПОЛУЧИТЬ ДОСТУП", callback_data="buy_subscription")],
        [InlineKeyboardButton(text="📊 МОЙ СТАТУС", callback_data="check_status")],
        [InlineKeyboardButton(text="💸 ПОПОЛНИТЬ БАЛАНС", callback_data="balance_topup")],
        [InlineKeyboardButton(text="🤝 РЕФЕРАЛЬНАЯ СХЕМА", callback_data="referral_menu")],
        [InlineKeyboardButton(text="🎁 ПРОМОКОД", callback_data="activate_promo")],
        [InlineKeyboardButton(text="🆘 ПОДДЕРЖКА", callback_data="support")]
    ])


def tariff_keyboard() -> InlineKeyboardMarkup:
    """Выбор тарифа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"30 дней — {settings.price_30_days}₽",
            callback_data="tariff_30"
        )],
        [InlineKeyboardButton(
            text=f"90 дней — {settings.price_90_days}₽",
            callback_data="tariff_90"
        )],
        [InlineKeyboardButton(
            text=f"180 дней — {settings.price_180_days}₽",
            callback_data="tariff_180"
        )],
        [InlineKeyboardButton(text="◀ НАЗАД", callback_data="back_to_menu")]
    ])


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ В МЕНЮ", callback_data="back_to_menu")]
    ])


def payment_keyboard(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 ОПЛАТИТЬ", url=pay_url)],
        [InlineKeyboardButton(text="✅ ПРОВЕРИТЬ ОПЛАТУ", callback_data="check_payment")],
        [InlineKeyboardButton(text="◀ НАЗАД", callback_data="back_to_menu")]
    ])


def topup_amounts_keyboard() -> InlineKeyboardMarkup:
    """Суммы пополнения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="100₽", callback_data="topup_100"),
            InlineKeyboardButton(text="300₽", callback_data="topup_300")
        ],
        [
            InlineKeyboardButton(text="500₽", callback_data="topup_500"),
            InlineKeyboardButton(text="1000₽", callback_data="topup_1000")
        ],
        [InlineKeyboardButton(text="◀ НАЗАД", callback_data="back_to_menu")]
    ])


def subscription_link_keyboard(link: str) -> InlineKeyboardMarkup:
    """Ссылка на подписку"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 ПОДКЛЮЧИТЬСЯ", url=link)],
        [InlineKeyboardButton(text="◀ В МЕНЮ", callback_data="back_to_menu")]
    ])
