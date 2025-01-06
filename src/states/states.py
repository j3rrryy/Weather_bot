from aiogram.fsm.state import State, StatesGroup


class FSMSettings(StatesGroup):
    set_location = State()
    unit_of_temp = State()
    unit_of_wind = State()


class FSMLanguage(StatesGroup):
    set_language = State()
