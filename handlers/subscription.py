from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
from database import get_user, update_balance, update_subscription_end
from remnawave import remnawave
from keyboards.inline import tariff_keyboard, subscription_link_keyboard, back_to_menu_keyboard
from texts import (
    CHOOSE_TARIFF, SUBSCRIPTION_ACTIVE, NO_SUBSCRIPTION,
    SUBSCRIPTION_BUY_SUCCESS, SUBSCRIPTION_EXPIRED
)
from config import settings

router = Router()


@router.callback_query(F.data == "buy_subscription")
async def choose_tariff(callback: CallbackQuery):
    """Выбор тарифа"""
    await callback.message.edit_text(
        CHOOSE_TARIFF,
        parse_mode="Markdown",
        reply_markup=tariff_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "check_status")
async def check_status(callback: CallbackQuery):
    """Проверка статуса подписки"""
    user = await get_user(callback.from_user.id)
    
    if not user or not user.get("subscription_end"):
        await callback.message.edit_text(
            NO_SUBSCRIPTION,
            parse_mode="Markdown",
            reply_markup=tariff_keyboard()
        )
        await callback.answer()
        return
    
    end_date = datetime.fromisoformat(user["subscription_end"])
    now = datetime.now()
    days_left = (end_date - now).days
    
    if days_left < 0:
        text = SUBSCRIPTION_EXPIRED
    else:
        text = SUBSCRIPTION_ACTIVE.format(
            days_left=days_left,
            traffic="Безлимит",
            devices=3
        )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tariff_"))
async def buy_tariff(callback: CallbackQuery):
    """Покупка тарифа"""
    days = int(callback.data.split("_")[1])
    price_map = {
        30: settings.price_30_days,
        90: settings.price_90_days,
        180: settings.price_180_days
    }
    price = price_map[days]
    
    user = await get_user(callback.from_user.id)
    
    # Проверяем баланс
    if user["balance"] < price:
        await callback.message.edit_text(
            f"❌ **МАЛО ДЕНЕГ**\n\n"
            f"Нужно: {price}₽\n"
            f"У тебя: {user['balance']}₽\n\n"
            f"Пополни баланс и возвращайся.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Списываем деньги
    await update_balance(callback.from_user.id, -price, f"Покупка подписки на {days} дней")
    
    # Создаем или продлеваем подписку в Remnawave
    try:
        if user.get("remnawave_uuid"):
            result = await remnawave.extend_subscription(user["remnawave_uuid"], days)
        else:
            result = await remnawave.create_user(callback.from_user.id, callback.from_user.username, days)
        
        # Вычисляем новую дату окончания
        if user.get("subscription_end"):
            current_end = datetime.fromisoformat(user["subscription_end"])
            if current_end < datetime.now():
                new_end = datetime.now() + timedelta(days=days)
            else:
                new_end = current_end + timedelta(days=days)
        else:
            new_end = datetime.now() + timedelta(days=days)
        
        remnawave_uuid = result.get("uuid", user.get("remnawave_uuid", ""))
        await update_subscription_end(callback.from_user.id, new_end, remnawave_uuid)
        
        # Получаем ссылку для подключения
        link = await remnawave.get_subscription_link(remnawave_uuid)
        
        await callback.message.edit_text(
            SUBSCRIPTION_BUY_SUCCESS.format(
                days=days,
                end_date=new_end.strftime("%d.%m.%Y %H:%M")
            ),
            parse_mode="Markdown",
            reply_markup=subscription_link_keyboard(link)
        )
    except Exception as e:
        # Возвращаем деньги если что-то пошло не так
        await update_balance(callback.from_user.id, price, "Возврат средств")
        await callback.message.edit_text(
            "⚠️ **СБОЙ В МАТРИЦЕ**\n\n"
            f"Ошибка: {str(e)}\n\n"
            "Деньги возвращены. Попробуй позже или пиши в поддержку.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard()
        )
    
    await callback.answer()
