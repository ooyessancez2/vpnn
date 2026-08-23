from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, update_balance
from payments import cryptobot
from keyboards.inline import topup_amounts_keyboard, payment_keyboard, back_to_menu_keyboard
from texts import BALANCE_MESSAGE, TOPUP_AMOUNT, PAYMENT_INSTRUCTIONS, PAYMENT_SUCCESS

router = Router()


class TopUpStates(StatesGroup):
    waiting_amount = State()


@router.callback_query(F.data == "balance_topup")
async def show_balance(callback: CallbackQuery):
    """Показать баланс"""
    user = await get_user(callback.from_user.id)
    text = BALANCE_MESSAGE.format(balance=user["balance"])
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=topup_amounts_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topup_"))
async def topup_amount(callback: CallbackQuery, state: FSMContext):
    """Выбор суммы пополнения"""
    amount = int(callback.data.split("_")[1])
    
    try:
        invoice = await cryptobot.create_invoice(
            amount=amount,
            description="Пополнение баланса VPN",
            telegram_id=callback.from_user.id
        )
        await state.update_data(amount=amount, invoice_id=invoice["invoice_id"])
        
        text = PAYMENT_INSTRUCTIONS.format(amount=amount)
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(invoice["pay_url"])
        )
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ **ОШИБКА ОПЛАТЫ**\n\n"
            f"Не удалось создать инвойс: {str(e)}\n\n"
            f"Попробуй позже или пиши в поддержку.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery, state: FSMContext):
    """Проверка оплаты (упрощенная версия)"""
    data = await state.get_data()
    amount = data.get("amount", 0)
    
    # В реальном боте здесь был бы запрос к API CryptoBot
    # Для демо просто начисляем баланс
    if amount > 0:
        new_balance = await update_balance(callback.from_user.id, amount, "Пополнение через CryptoBot")
        await callback.message.edit_text(
            PAYMENT_SUCCESS + f"\n\n💰 **НОВЫЙ БАЛАНС: {new_balance}₽**",
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
        await state.clear()
    else:
        await callback.answer("Сначала выбери сумму", show_alert=True)
