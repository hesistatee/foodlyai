from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Tariff


async def get_tariffs_keyboard(session: AsyncSession) -> InlineKeyboardMarkup:
    result = await session.execute(select(Tariff).order_by(Tariff.price))
    tariffs = result.scalars().all()

    keyboard_buttons: list[list[InlineKeyboardButton]] = []

    for tariff in tariffs:
        button_text = f"💰 {tariff.name} - {tariff.price} руб./{tariff.days} дней"

        button = InlineKeyboardButton(
            text=button_text, callback_data=f"tariff_{tariff.id}"
        )

        keyboard_buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
