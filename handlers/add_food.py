import logging

from aiogram import F, Router
from aiogram.types import Message

from database.models import User
from keyboards import add_food_keyboard
from static.texts import ADD_FOOD_TEXT
from utils.decorators import (
    fitness_profile_required,
    login_required,
    subscribe_required,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == ADD_FOOD_TEXT)
@login_required
@subscribe_required
@fitness_profile_required
async def add_food(message: Message, user: User):
    keyboard = add_food_keyboard
    await message.answer(
        "Выбери каки способом хочешь добавить продукт", reply_markup=keyboard
    )
