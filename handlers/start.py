from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from static.texts import WELCOME_TEXT
from utils.keyboards import choose_action_kb
from database.repositories import user_repository

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await user_repository.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    
    await message.answer(
        WELCOME_TEXT,
        reply_markup=choose_action_kb
    )