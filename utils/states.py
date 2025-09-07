from aiogram.filters.state import State, StatesGroup

class MainGroup(StatesGroup):
    analyze_product_composition_state = State()
    count_the_number_of_calories_state = State()