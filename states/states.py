from aiogram.fsm.state import State, StatesGroup


class FSMSettings(StatesGroup):

    # set user location
    set_location = State()

    # set temperature measurement unit
    unit_of_temp = State()

    # set wind speed measurement unit
    unit_of_wind = State()


class FSMLanguage(StatesGroup):

    # set user language
    set_language = State()
