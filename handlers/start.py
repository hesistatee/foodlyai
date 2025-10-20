from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.repositories import UserRepository
from static.texts import WELCOME_TEXT
from utils.keyboards import choose_analyze_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    telegram_id = message.from_user.id
    username = message.from_user.username
    repo = UserRepository(session=session)

    _, create = await repo.get_or_create_user(
        telegram_id=telegram_id, username=username
    )
    if create:
        await repo.update_subscription(
            telegram_id=telegram_id, days=settings.TRIAL_DAYS
        )

    await message.answer(
        WELCOME_TEXT, parse_mode="HTML", reply_markup=choose_analyze_kb
    )
