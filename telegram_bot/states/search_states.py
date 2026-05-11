from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    region = State()
    score = State()
    direction = State()
    education_type = State()
