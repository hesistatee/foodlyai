import logging
from datetime import date

from aiogram import F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards import get_food_history_keyboard, get_progress_keyboard
from static.texts import MY_PROGRESS_TEXT
from utils.decorators import (
    fitness_profile_required,
    login_required,
    subscribe_required,
)
from utils.text_generators import get_food_history_text, get_progress_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == MY_PROGRESS_TEXT)
@login_required
@subscribe_required
@fitness_profile_required
async def my_progress(message: Message, user: User, session: AsyncSession):
    text = await get_progress_text(session=session, user=user)
    keyboard = await get_progress_keyboard()

    if text and keyboard:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "food_history")
async def food_history(callback: CallbackQuery, session: AsyncSession, user: User):
    food_history_text = await get_food_history_text(session=session, user=user)
    keyboard = await get_food_history_keyboard()

    if (
        food_history_text
        and keyboard
        and callback.message
        and not isinstance(callback.message, InaccessibleMessage)
    ):
        await callback.message.edit_text(food_history_text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(F.data == "back_to_my_progress")
async def back_to_my_progress(
    callback: CallbackQuery, session: AsyncSession, user: User
):
    progress_text = await get_progress_text(session=session, user=user)
    keyboard = await get_progress_keyboard()

    if (
        progress_text
        and keyboard
        and callback.message
        and not isinstance(callback.message, InaccessibleMessage)
    ):
        await callback.message.edit_text(progress_text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(F.data.startswith("food_date:"))
async def change_food_history_date(
    callback: CallbackQuery, session: AsyncSession, user: User
):
    if callback.data and callback.message:
        selected_date_str = callback.data.split(":")[1]
        selected_date = date.fromisoformat(selected_date_str)

        food_history_text = await get_food_history_text(
            session=session, user=user, selected_date=selected_date
        )
        keyboard = await get_food_history_keyboard(selected_date=selected_date)

        if (
            food_history_text
            and keyboard
            and not isinstance(callback.message, InaccessibleMessage)
        ):
            await callback.message.edit_text(food_history_text, reply_markup=keyboard)
            await callback.answer()


@router.callback_query(F.data.startswith("progress_date:"))
async def change_progress_date(
    callback: CallbackQuery, session: AsyncSession, user: User
):
    if callback.data and callback.message:
        selected_date_str = callback.data.split(":")[1]
        selected_date = date.fromisoformat(selected_date_str)

        progress_text = await get_progress_text(
            session=session, user=user, selected_date=selected_date
        )
        keyboard = await get_progress_keyboard(selected_date)

        if (
            progress_text
            and keyboard
            and not isinstance(callback.message, InaccessibleMessage)
        ):
            await callback.message.edit_text(progress_text, reply_markup=keyboard)
            await callback.answer()
