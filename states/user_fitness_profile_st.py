from aiogram.fsm.state import State, StatesGroup


class UserFitnessProfile(StatesGroup):
    current_weight_state: State = State()
    desired_weight_state: State = State()
    height_state: State = State()
    age_state: State = State()
    gender_state: State = State()
