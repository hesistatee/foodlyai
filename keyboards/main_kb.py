from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from static.texts import (
    ADD_FOOD_TEXT,
    MY_PROGRESS_TEXT,
    SCAN_PRODUCT_COMPOSITION_TEXT,
    SUBSCRIBE_STATUS_TEXT,
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=MY_PROGRESS_TEXT),
            KeyboardButton(text=ADD_FOOD_TEXT),
        ],
        [
            KeyboardButton(text=SCAN_PRODUCT_COMPOSITION_TEXT),
            KeyboardButton(text=SUBSCRIBE_STATUS_TEXT),
        ],
    ],
    resize_keyboard=True,
)
