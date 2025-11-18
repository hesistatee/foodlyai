from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from static.texts import (
    CHOOSE_TARIFF_TEXT,
    EXTEND_TEXT,
)

subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=CHOOSE_TARIFF_TEXT, callback_data="choose_tariff"
            ),
            InlineKeyboardButton(text=EXTEND_TEXT, callback_data="extend"),
        ]
    ]
)
