from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from static.texts import WELCOME_TEXT
from utils.keyboards import choose_action_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        WELCOME_TEXT,
        reply_markup=choose_action_kb
    )