from aiogram import Bot, Router, F
from aiogram.types import Message, ReplyKeyboardRemove,\
    CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from lexicon import LEXICON_RU, LEXICON_EN, LEXICON_BOTH,\
    ERROR_LEXICON_RU, ERROR_LEXICON_EN, ERROR_LEXICON_BOTH
from services import create_forecast_today,\
    create_forecast_week, create_profile, create_plot
from keyboards import language_kb, location_kb, temp_kb,\
    wind_kb, weather_kb, days_kb, back_kb, plots_kb
from states import FSMSettings, FSMLanguage
from database import get_data, post_lang, update_data, get_language
from errors import DataError, GetWeatherError


router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext):
    """
    Send the start message and starts the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/start'], reply_markup=language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['help']), StateFilter(default_state))
async def help_command(message: Message):
    """
    Send the help messasge.
    """

    if get_language(message.from_user.id) == 'RU':
        await message.answer(LEXICON_RU['/help'])
    else:
        await message.answer(LEXICON_EN['/help'])


@router.message(Command(commands=['settings']), StateFilter(default_state))
async def settings_command(message: Message, state: FSMContext):
    """
    Start the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/settings'], reply_markup=language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['weather']), StateFilter(default_state))
async def weather_command(message: Message):
    """
    Send a message which allows the user to choose the weather forecast mode.
    """
    try:
        if get_language(message.from_user.id) == 'RU':
            await message.answer(LEXICON_RU['/weather'], reply_markup=weather_kb('RU'))
        else:
            await message.answer(LEXICON_EN['/weather'], reply_markup=weather_kb('EN'))

    except DataError as e:
        print(e)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.message(Command(commands=['profile']), StateFilter(default_state))
async def get_profile(message: Message):
    """
    Send the user profile.
    """

    try:
        data: dict[str, str | float] = get_data(message.from_user.id)
        if get_language(message.from_user.id) == 'RU':
            await message.answer(f'{LEXICON_RU["your_profile"]}\n\n{create_profile(data, "RU")}')
        else:
            await message.answer(f'{LEXICON_EN["your_profile"]}\n\n{create_profile(data, "EN")}')

    except DataError as e:
        print(e)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.callback_query(StateFilter(FSMLanguage.set_language))
async def language(callback: CallbackQuery, state: FSMContext):
    """
    Set the user language snd sends a message
    which allows the user to set his location.
    """

    await state.update_data(language=callback.data)

    await callback.answer()

    try:
        post_lang(data=(callback.from_user.id, (await state.get_data())['language']))

    except DataError as e:
        print(e)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.clear()

    if get_language(callback.from_user.id) == 'RU':
        await callback.message.answer(LEXICON_RU['lang_success'], reply_markup=location_kb('RU'))
    else:
        await callback.message.answer(LEXICON_EN['lang_success'], reply_markup=location_kb('EN'))

    await state.set_state(FSMSettings.set_location)


@router.message(F.location, StateFilter(FSMSettings.set_location))
async def location(message: Message, state: FSMContext):
    """
    Set the user location and sends a message
    which allows the user to select temperature measurement units.
    """

    await state.update_data(latitude=message.location.latitude,
                            longitude=message.location.longitude)

    if get_language(message.from_user.id) == 'RU':
        await message.answer(LEXICON_RU['loc_success'], reply_markup=temp_kb())
    else:
        await message.answer(LEXICON_EN['loc_success'], reply_markup=temp_kb())

    await state.set_state(FSMSettings.unit_of_temp)


@router.callback_query(StateFilter(FSMSettings.unit_of_temp),
                       Text(text=['celsius', 'fahrenheit']))
async def unit_of_temp(callback: CallbackQuery, state: FSMContext):
    """
    Set the user temperature measurement units and sends a message
    which allows the user to select wind speed measurement units.
    """

    await state.update_data(temp_unit=callback.data)

    await callback.answer()

    if get_language(callback.from_user.id) == 'RU':
        await callback.message.edit_text(LEXICON_RU['temp_success'], reply_markup=wind_kb('RU'))
    else:
        await callback.message.edit_text(LEXICON_EN['temp_success'], reply_markup=wind_kb('EN'))

    await state.set_state(FSMSettings.unit_of_wind)


@router.callback_query(StateFilter(FSMSettings.unit_of_wind),
                       Text(text=['mps', 'kmph']))
async def unit_of_wind(callback: CallbackQuery, state: FSMContext):
    """
    Set the user wind speed measurement units and sends a message
    about the completed configuration procedure.
    """

    await state.update_data(wind_unit=callback.data)

    await callback.answer()

    if get_language(callback.from_user.id) == 'RU':
        await callback.message.answer(LEXICON_RU['settings_completed'],
                                      reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    else:
        await callback.message.answer(LEXICON_EN['settings_completed'],
                                      reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

    update_data(data=(callback.from_user.id, await state.get_data()))

    await state.clear()


@router.callback_query(StateFilter(default_state),
                       Text(text=['forecast_today']))
async def get_forecast_today(callback: CallbackQuery):
    """
    Send weather forecast for today.
    """

    await callback.answer()

    try:
        lang = get_language(callback.from_user.id)
        res: str = await create_forecast_today(callback.from_user.id, lang)
        if lang == 'RU':
            await callback.message.edit_text(f'{LEXICON_RU["weather_today"]}{res}')
        else:
            await callback.message.edit_text(f'{LEXICON_EN["weather_today"]}{res}')

    except DataError as e:
        print(e)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as e:
        print(e)
        if get_language(callback.from_user.id) == 'RU':
            await callback.message.edit_text(ERROR_LEXICON_RU['GetWeatherError'])
        else:
            await callback.message.edit_text(ERROR_LEXICON_EN['GetWeatherError'])


@router.callback_query(StateFilter(default_state),
                       Text(text=['forecast_week', 'back']))
async def week_forecast_days(callback: CallbackQuery):
    """
    Send a message which allows the user to choose the weather forecast
    for a certain day or to choose the weather plots mode.
    """

    await callback.answer()

    lang = get_language(callback.from_user.id)

    if lang == 'RU':
        await callback.message.edit_text(LEXICON_RU["weather_week"], reply_markup=days_kb(lang, callback.from_user.id))
    else:
        await callback.message.edit_text(LEXICON_EN["weather_week"], reply_markup=days_kb(lang, callback.from_user.id))


@router.callback_query(StateFilter(default_state),
                       Text(text=[str(day).zfill(2) for day in range(1, 32)]))
async def get_forecast_week(callback: CallbackQuery):
    """
    Send weather forecast for the following day.
    """

    await callback.answer()

    try:
        lang = get_language(callback.from_user.id)
        res: dict[str, str] = await create_forecast_week(callback.from_user.id, lang)
        if lang == 'RU':
            await callback.message.edit_text(res[callback.data], # type: ignore
                                             reply_markup=back_kb('RU'))
        else:
            await callback.message.edit_text(res[callback.data], # type: ignore
                                             reply_markup=back_kb('EN'))

    except DataError as e:
        print(e)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as e:
        print(e)
        lang = get_language(callback.from_user.id)
        if lang == 'RU':
            await callback.message.edit_text(ERROR_LEXICON_RU['GetWeatherError'])
        else:
            await callback.message.edit_text(ERROR_LEXICON_EN['GetWeatherError'])


@router.callback_query(StateFilter(default_state),
                       Text(text='plots'))
async def get_plots(callback: CallbackQuery):
    """
    Send the weather plots list.
    """

    await callback.answer()

    try:
        if get_language(callback.from_user.id) == 'RU':
            await callback.message.edit_text(LEXICON_RU['plots'],
                                             reply_markup=plots_kb('RU'))
        else:
            await callback.message.edit_text(LEXICON_EN['plots'],
                                             reply_markup=plots_kb('EN'))
    except DataError as e:
        print(e)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])


@router.callback_query(StateFilter(default_state),
                       Text(text=['temp', 'wind', 'precip', 'humid']))
async def get_plot(callback: CallbackQuery, bot: Bot):
    """
    Send a weather plot.
    """

    await callback.answer()

    try:
        user_id = callback.from_user.id
        lang = get_language(user_id)
        await create_plot(user_id, lang, callback.data) # type: ignore

        if lang == 'RU':
            await bot.send_photo(chat_id=callback.message.chat.id,
                                 photo=FSInputFile(fr'./services/{user_id}_plot.png'))
        else:
            await bot.send_photo(chat_id=callback.message.chat.id,
                                 photo=FSInputFile(fr'./services/{user_id}_plot.png'))

    except DataError as e:
        print(e)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as e:
        print(e)
        lang = get_language(callback.from_user.id)
        if lang == 'RU':
            await callback.message.edit_text(ERROR_LEXICON_RU['GetWeatherError'])
        else:
            await callback.message.edit_text(ERROR_LEXICON_EN['GetWeatherError'])


@router.message()
async def unknown(message: Message):
    """
    Send a message that it can not understand the user.
    """

    await message.answer(LEXICON_BOTH['unknown'])
