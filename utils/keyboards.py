from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from static.texts import SCAN_PRODUCT_COMPOSITION_TEXT, COUNT_THE_NUMBER_OF_CALORIES_TEXT, SUBSCRIBE_STATUS_TEXT, CHOOSE_TARIFF_TEXT, EXTEND_TEXT
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Tariff
from sqlalchemy import select

choose_analyze_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SCAN_PRODUCT_COMPOSITION_TEXT), KeyboardButton(text=COUNT_THE_NUMBER_OF_CALORIES_TEXT)],
        [KeyboardButton(text=SUBSCRIBE_STATUS_TEXT)]
    ],
    resize_keyboard=True
)

subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=CHOOSE_TARIFF_TEXT, callback_data="choose_tariff"), InlineKeyboardButton(text=EXTEND_TEXT, callback_data="extend")]
    ]
)

async def get_tariffs_keyboard(session: AsyncSession) -> InlineKeyboardMarkup:
    result = await session.execute(select(Tariff))
    tariffs = result.scalars().all()
    
    keyboard_buttons = []
    
    for tariff in tariffs:
        button_text = f"💰 {tariff.name} - {tariff.price} руб./{tariff.days} дней"
        
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"tariff_{tariff.id}"
        )
        
        keyboard_buttons.append([button])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
