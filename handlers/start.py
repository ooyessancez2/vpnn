from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database import get_user, create_user
from keyboards.inline import main_menu_keyboard
from texts import START_MESSAGE, MENU_MESSAGE

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик /start"""
    telegram_id = message.from_user.id
    username = message.from_user.username or "unknown"
    
    # Проверяем реферальный код
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        try:
            referrer_id = int(message.text.split()[1])
        except ValueError:
            pass
    
    # Создаем пользователя если его нет
    user = await get_user(telegram_id)
    if not user:
        await create_user(telegram_id, username, referrer_id)
    
    await message.answer(
        START_MESSAGE,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        MENU_MESSAGE,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
