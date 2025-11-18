from aiogram import F, Router
from aiogram.types import Message

from database.models import User
from keyboards import subscription_keyboard
from static.texts import SUBSCRIBE_STATUS_TEXT
from utils.decorators import login_required

router = Router()


@router.message(F.text == SUBSCRIBE_STATUS_TEXT)
@login_required
async def check_subscription_status(message: Message, user: User) -> None:
    if user:
        if user.is_admin:
            await message.answer(
                "🎯 Вы администратор\nВам доступно неограниченное количество запросов",
                reply_markup=subscription_keyboard,
            )
        elif not user.subscription_is_active:
            await message.answer(
                "❌ Срок вашей подписки истек\n\n"
                "Для продолжения работы выберите подходящий тариф👇",
                reply_markup=subscription_keyboard,
            )
        else:
            end_date = user.subscription_end
            formatted_date = end_date.strftime("%d.%m.%Y в %H:%M")

            await message.answer(
                f"✅ Ваша подписка активна\n"
                f"Действует до: {formatted_date}\n\n"
                f"Вы можете выбрать другой тариф или продлить текущий👇",
                reply_markup=subscription_keyboard,
            )
