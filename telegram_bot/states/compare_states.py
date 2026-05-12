from aiogram.fsm.state import State, StatesGroup


class CompareStates(StatesGroup):
    choosing_items = State()
