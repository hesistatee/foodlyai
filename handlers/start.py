from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.repositories import UserRepository
from keyboards import main_kb
from static.texts import WELCOME_TEXT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if message.from_user:
        telegram_id = message.from_user.id
        username = message.from_user.username
        repo = UserRepository(session=session)

        user, create = await repo.get_or_create_user(
            telegram_id=telegram_id, username=username
        )
        if create:
            await repo.update_subscription(user=user, days=settings.TRIAL_DAYS)

        await message.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=main_kb)
