from aiogram import Router, F
from aiogram.types import Message
from static.texts import SUBSCRIBE_STATUS_TEXT
from utils.keyboards import subscription_keyboard
from database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(F.text == SUBSCRIBE_STATUS_TEXT)
async def check_subscription_status(message: Message, session: AsyncSession) -> None:
    tg_id = message.from_user.id
    repo = UserRepository(session=session)
    
    user = await repo.get_user(telegram_id=tg_id)
    
    if not user:
        await message.answer(
            "👋 Привет! Кажется, мы еще не знакомы.\n"
            "Для начала работы воспользуйтесь командой /start"
        )
        return
    
    if user.is_admin:
        await message.answer(
            "🎯 Вы администратор\n"
            "Вам доступно неограниченное количество запросов",
            reply_markup=subscription_keyboard
        )
    elif not await repo.check_subscription_active(telegram_id=tg_id):
        await message.answer(
            "❌ Срок вашей подписки истек\n\n"
            "Для продолжения работы выберите подходящий тариф👇",
            reply_markup=subscription_keyboard
        )
    else:
        end_date = user.subscription_end
        formatted_date = end_date.strftime("%d.%m.%Y в %H:%M")
                                           
        await message.answer(
            f"✅ Ваша подписка активна\n"
            f"Действует до: {formatted_date}\n\n"
            f"Вы можете выбрать другой тариф или продлить текущий👇",
            reply_markup=subscription_keyboard
        )
    