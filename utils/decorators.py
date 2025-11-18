from functools import wraps

from aiogram.types import CallbackQuery, Message

from keyboards import subscription_keyboard
from states import UserFitnessProfile


def login_required(func):
    @wraps(func)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        if "user" not in kwargs:
            await event.answer(
                "👋 Привет! Кажется, мы еще не знакомы.\nДля начала работы воспользуйтесь командой /start"
            )
            return
        return await func(event, *args, **kwargs)

    return wrapper


def subscribe_required(func):
    @wraps(func)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user = kwargs.get("user")
        if user:
            if user.subscription_is_active and not user.is_admin:
                await event.answer(
                    "⚠️ Ваша подписка завершилась\n\nЧтобы продолжить пользоваться всеми возможностями, пожалуйста, продлите подписку 💫",
                    reply_markup=subscription_keyboard,
                )
                return
        return await func(event, *args, **kwargs)

    return wrapper


def fitness_profile_required(func):
    @wraps(func)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user = kwargs.get("user")
        state = kwargs.get("state")
        if user and state:
            if not user.fitness_profile:
                await state.set_state(UserFitnessProfile.current_weight_state)
                await event.answer(
                    "Для того что бы показать прогресс, нам надо заполнить данные о вас"
                )
                await event.answer("Введите свой текущий вес:")
                return
        return await func(event, *args, **kwargs)

    return wrapper
