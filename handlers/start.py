from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from static.texts import WELCOME_TEXT
from utils.keyboards import choose_action_kb
from database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from config import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    telegram_id = message.from_user.id
    repo = UserRepository(session=session)
    
    user, create = await repo.get_or_create_user(
        telegram_id=telegram_id,
        username=message.from_user.username
    )
    if create:
        await repo.update_subscription(telegram_id=telegram_id, days=config.TRIAL_DAYS)
    
    await message.answer(
        WELCOME_TEXT,
        parse_mode='HTML',
        reply_markup=choose_action_kb
    )