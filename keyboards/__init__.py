from .add_food_kb import add_food_keyboard
from .food_history_kb import get_food_history_keyboard
from .main_kb import main_kb
from .progress_kb import get_progress_keyboard
from .subscription_kb import subscription_keyboard
from .tariffs_kb import get_tariffs_keyboard

__all__ = [
    "get_food_history_keyboard",
    "main_kb",
    "get_progress_keyboard",
    "subscription_keyboard",
    "get_tariffs_keyboard",
    "add_food_keyboard",
]
