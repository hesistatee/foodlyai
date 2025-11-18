from datetime import date, timedelta

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def get_food_history_keyboard(
    selected_date: date = date.today(),
) -> InlineKeyboardMarkup:
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️", callback_data=f"food_date:{prev_date}"),
                InlineKeyboardButton(
                    text=selected_date.strftime("%d.%m"), callback_data="current_date"
                ),
                InlineKeyboardButton(text="▶️", callback_data=f"food_date:{next_date}"),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_my_progress",
                )
            ],
        ]
    )

    return keyboard
