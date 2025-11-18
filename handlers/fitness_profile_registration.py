import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import FitnessProfileRepository
from states import UserFitnessProfile
from utils.validators import (
    validate_age,
    validate_gender,
    validate_height,
    validate_weight,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(UserFitnessProfile.current_weight_state)
async def process_current_weight(message: Message, state: FSMContext, user: User):
    current_weight = message.text.strip() if message.text else None
    if current_weight:
        if not validate_weight(current_weight):
            await message.answer("Неккоректно введен вес")
            return
        await state.update_data(current_weight=int(current_weight))
        await state.set_state(UserFitnessProfile.desired_weight_state)
        await message.answer("Введите желаемый вес:")


@router.message(UserFitnessProfile.desired_weight_state)
async def process_desired_weight(message: Message, state: FSMContext, user: User):
    desired_weight = message.text.strip() if message.text else None
    if desired_weight:
        if not validate_weight(desired_weight):
            await message.answer("Неккоректно введен вес")
            return
        await state.update_data(desired_weight=int(desired_weight))
        await state.set_state(UserFitnessProfile.height_state)
        await message.answer("Введите свой рост:")


@router.message(UserFitnessProfile.height_state)
async def process_height(message: Message, state: FSMContext, user: User):
    height = message.text.strip() if message.text else None
    if height:
        if not validate_height(height):
            await message.answer("Неккоректно введен рост")
            return
        await state.update_data(height=int(height))
        await state.set_state(UserFitnessProfile.age_state)
        await message.answer("Введите свой возраст:")


@router.message(UserFitnessProfile.age_state)
async def process_age(message: Message, state: FSMContext, user: User):
    age = message.text.strip() if message.text else None
    if age:
        if not validate_age(age):
            await message.answer("Неккоректно введен возраст")
            return
        await state.update_data(age=int(age))
        await state.set_state(UserFitnessProfile.gender_state)
        await message.answer("Введите свой пол:")


@router.message(UserFitnessProfile.gender_state)
async def process_gender(
    message: Message, state: FSMContext, session: AsyncSession, user: User
):
    gender = message.text.strip() if message.text else None

    if gender:
        if not validate_gender(gender):
            await message.answer("Неккоректно введен пол")
            return
        await state.update_data(gender=gender)
        try:
            fp_repo = FitnessProfileRepository(session=session)
            data = await state.get_data()
            if user:
                await fp_repo.create_fitness_profile(user_id=user.id, **data)
                await state.clear()
                await message.answer("Профиль успешно создан")
        except Exception as e:
            logger.error(f"Error creating fitness profile: {e}")
            await message.answer("Ошибка при создании профиля")
            await state.clear()
            await message.answer("Попробуйте еще раз")
