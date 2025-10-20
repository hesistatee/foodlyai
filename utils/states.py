from aiogram.fsm.state import State, StatesGroup


class MainGroup(StatesGroup):
    analyze_product_composition_state: State = State()
    count_the_number_of_calories_state: State = State()
