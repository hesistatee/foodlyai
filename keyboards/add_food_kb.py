from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from static.texts import FROM_ARCHIVE_TEXT, MANUALLY_TEXT, PARSE_PRODUCT_TEXT

add_food_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=MANUALLY_TEXT, callback_data="manually"),
            InlineKeyboardButton(
                text=PARSE_PRODUCT_TEXT, callback_data="parse_product"
            ),
        ],
        [InlineKeyboardButton(text=FROM_ARCHIVE_TEXT, callback_data="from_archive")],
    ]
)
