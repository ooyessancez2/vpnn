from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_user, get_referral_stats
from keyboards.inline import back_to_menu_keyboard
from texts import REFERRAL_MESSAGE
from config import settings

router = Router()


@router.callback_query(F.data == "referral_menu")
async def referral_menu(callback: CallbackQuery):
    """Меню реферальной программы"""
    stats = await get_referral_stats(callback.from_user.id)
    bot_username = (await callback.bot.get_me()).username
    
    text = REFERRAL_MESSAGE.format(
        bonus=settings.referral_bonus_rub,
        referral_link=f"https://t.me/{bot_username}?start={callback.from_user.id}",
        referrals_count=stats["count"],
        earnings=stats["count"] * settings.referral_bonus_rub
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard()
    )
    await callback.answer()
