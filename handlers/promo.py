from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import activate_promo_code
from keyboards.inline import back_to_menu_keyboard
from texts import PROMO_SUCCESS, PROMO_FAILED

router = Router()


class PromoStates(StatesGroup):
    waiting_code = State()


@router.callback_query(F.data == "activate_promo")
async def ask_promo_code(callback: CallbackQuery, state: FSMContext):
    """Запрос промокода"""
    await callback.message.edit_text(
        "🎁 **ВВЕДИ ПРОМОКОД**\n\n"
        "Напиши его сюда. Без пробелов и лишних символов.",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard()
    )
    await state.set_state(PromoStates.waiting_code)
    await callback.answer()


@router.message(PromoStates.waiting_code)
async def process_promo_code(message: Message, state: FSMContext):
    """Обработка промокода"""
    code = message.text.strip().upper()
    bonus = await activate_promo_code(message.from_user.id, code)
    
    if bonus:
        await message.answer(
            PROMO_SUCCESS.format(bonus=bonus),
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await message.answer(
            PROMO_FAILED,
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
    
    await state.clear()
