from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from static.texts import SCAN_PRODUCT_COMPOSITION_TEXT, COUNT_THE_NUMBER_OF_CALORIES_TEXT

choose_action_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SCAN_PRODUCT_COMPOSITION_TEXT), KeyboardButton(text=COUNT_THE_NUMBER_OF_CALORIES_TEXT)]
    ],
    resize_keyboard=True
)