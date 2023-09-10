import os

from aiogram import Bot, Router, F
from aiogram.types import Message, ReplyKeyboardRemove,\
    CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from lexicon import LEXICON_RU, LEXICON_EN, LEXICON_BOTH,\
    ERROR_LEXICON_RU, ERROR_LEXICON_EN, ERROR_LEXICON_BOTH
from middlewares import AntiFloodMiddleware
from services import create_forecast_today,\
    create_forecast_week, create_profile, create_plot
from keyboards import language_kb, location_kb, temp_kb,\
    wind_kb, weather_kb, days_kb, back_kb, plots_kb
from states import FSMSettings, FSMLanguage
from database import post_lang, update_data, get_language
from errors import DataError, GetWeatherError


router: Router = Router()
router.message.middleware.register(AntiFloodMiddleware())


@router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext):
    """
    Send the start message and starts the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/start'], reply_markup=language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['help']), StateFilter(default_state))
async def help_command(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the help messasge.
    """
    try:
        if await get_language(user_id=message.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await message.answer(LEXICON_RU['/help'])
        else:
            await message.answer(LEXICON_EN['/help'])
    except DataError as error:
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.message(Command(commands=['settings']), StateFilter(default_state))
async def settings_command(message: Message, state: FSMContext):
    """
    Start the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/settings'], reply_markup=language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['weather']), StateFilter(default_state))
async def weather_command(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a message which allows the user to choose the weather forecast mode.
    """
    try:
        if await get_language(user_id=message.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await message.answer(LEXICON_RU['/weather'], reply_markup=weather_kb('RU'))
        else:
            await message.answer(LEXICON_EN['/weather'], reply_markup=weather_kb('EN'))

    except DataError as error:
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.message(Command(commands=['profile']), StateFilter(default_state))
async def get_profile(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the user profile.
    """

    try:
        if await get_language(user_id=message.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await message.answer(f'{LEXICON_RU["your_profile"]}\n\n{await create_profile(user_id=message.from_user.id, lang="RU", sessionmaker=sessionmaker)}')
        else:
            await message.answer(f'{LEXICON_EN["your_profile"]}\n\n{await create_profile(user_id=message.from_user.id, lang="EN", sessionmaker=sessionmaker)}')

    except DataError as error:
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.callback_query(StateFilter(FSMLanguage.set_language))
async def language(callback: CallbackQuery,
                   state: FSMContext,
                   sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Set the user language and sends a message
    which allows the user to set his location.
    """

    await state.update_data(language=callback.data)

    await callback.answer()

    try:
        await post_lang(data=(callback.from_user.id, (await state.get_data())['language']),
                        sessionmaker=sessionmaker)

    except DataError as error:
        await state.clear()
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.clear()

    try:
        if await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await callback.message.answer(LEXICON_RU['lang_success'], reply_markup=location_kb('RU'))
        else:
            await callback.message.answer(LEXICON_EN['lang_success'], reply_markup=location_kb('EN'))

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.set_state(FSMSettings.set_location)


@router.message(F.location, StateFilter(FSMSettings.set_location))
async def location(message: Message,
                   state: FSMContext,
                   sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Set the user location and sends a message
    which allows the user to select temperature measurement units.
    """

    await state.update_data(latitude=message.location.latitude,
                            longitude=message.location.longitude)

    try:
        if await get_language(user_id=message.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await message.answer(LEXICON_RU['loc_success'], reply_markup=temp_kb())
        else:
            await message.answer(LEXICON_EN['loc_success'], reply_markup=temp_kb())

    except DataError as error:
        await state.clear()
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])

    await state.set_state(FSMSettings.unit_of_temp)


@router.callback_query(StateFilter(FSMSettings.unit_of_temp),
                       Text(text=['celsius', 'fahrenheit']))
async def unit_of_temp(callback: CallbackQuery,
                       state: FSMContext,
                       sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Set the user temperature measurement units and sends a message
    which allows the user to select wind speed measurement units.
    """

    await state.update_data(temp_unit=callback.data)

    await callback.answer()

    try:
        if await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await callback.message.edit_text(LEXICON_RU['temp_success'], reply_markup=wind_kb('RU'))
        else:
            await callback.message.edit_text(LEXICON_EN['temp_success'], reply_markup=wind_kb('EN'))

    except DataError as error:
        await state.clear()
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.set_state(FSMSettings.unit_of_wind)


@router.callback_query(StateFilter(FSMSettings.unit_of_wind),
                       Text(text=['mps', 'kmph']))
async def unit_of_wind(callback: CallbackQuery,
                       state: FSMContext,
                       sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Set the user wind speed measurement units and sends a message
    about the completed configuration procedure.
    """

    await state.update_data(wind_unit=callback.data)

    await callback.answer()

    try:
        if await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await callback.message.answer(LEXICON_RU['settings_completed'],
                                          reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        else:
            await callback.message.answer(LEXICON_EN['settings_completed'],
                                          reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

    except DataError as error:
        await state.clear()
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    try:
        await update_data(data=(callback.from_user.id, await state.get_data()),
                          sessionmaker=sessionmaker)

    except DataError as error:
        await state.clear()
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.clear()


@router.callback_query(StateFilter(default_state),
                       Text(text=['forecast_today']))
async def get_forecast_today(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send weather forecast for today.
    """

    await callback.answer()

    try:
        lang = await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker)
        res: str = await create_forecast_today(user_id=callback.from_user.id,
                                               lang=lang,
                                               sessionmaker=sessionmaker)
        if lang == 'RU':
            await callback.message.edit_text(f'{LEXICON_RU["weather_today"]}{res}')
        else:
            await callback.message.edit_text(f'{LEXICON_EN["weather_today"]}{res}')

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        if await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await callback.message.edit_text(ERROR_LEXICON_RU['GetWeatherError'])
        else:
            await callback.message.edit_text(ERROR_LEXICON_EN['GetWeatherError'])


@router.callback_query(StateFilter(default_state),
                       Text(text=['forecast_week', 'back']))
async def week_forecast_days(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a message which allows the user to choose the weather forecast
    for a certain day or to choose the weather plots mode.
    """

    await callback.answer()

    lang = await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker)

    if lang == 'RU':
        await callback.message.edit_text(LEXICON_RU["weather_week"],
                                         reply_markup=await days_kb(user_id=callback.from_user.id,
                                                                    lang=lang,
                                                                    sessionmaker=sessionmaker))
    else:
        await callback.message.edit_text(LEXICON_EN["weather_week"],
                                         reply_markup=await days_kb(user_id=callback.from_user.id,
                                                                    lang=lang,
                                                                    sessionmaker=sessionmaker))


@router.callback_query(StateFilter(default_state),
                       Text(text=[str(day).zfill(2) for day in range(1, 32)]))
async def get_forecast_week(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send weather forecast for the following day.
    """

    await callback.answer()

    try:
        lang = await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker)
        res: dict[str, str] = await create_forecast_week(user_id=callback.from_user.id,
                                                         lang=lang,
                                                         sessionmaker=sessionmaker)
        if lang == 'RU':
            await callback.message.edit_text(res[callback.data],
                                             reply_markup=back_kb('RU'))
        else:
            await callback.message.edit_text(res[callback.data],
                                             reply_markup=back_kb('EN'))

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        lang = await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker)
        if lang == 'RU':
            await callback.message.edit_text(ERROR_LEXICON_RU['GetWeatherError'])
        else:
            await callback.message.edit_text(ERROR_LEXICON_EN['GetWeatherError'])


@router.callback_query(StateFilter(default_state),
                       Text(text='plots'))
async def get_plots(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the weather plots list.
    """

    await callback.answer()

    try:
        if await get_language(user_id=callback.from_user.id, sessionmaker=sessionmaker) == 'RU':
            await callback.message.edit_text(LEXICON_RU['plots'],
                                             reply_markup=plots_kb('RU'))
        else:
            await callback.message.edit_text(LEXICON_EN['plots'],
                                             reply_markup=plots_kb('EN'))
    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])


@router.callback_query(StateFilter(default_state),
                       Text(text=['temp', 'wind', 'precip', 'humid']))
async def get_plot(callback: CallbackQuery, bot: Bot, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a weather plot.
    """

    await callback.answer()

    try:
        user_id = callback.from_user.id
        file_path = fr'./services/temp/{user_id}_plot.png'
        lang = await get_language(user_id=user_id, sessionmaker=sessionmaker)

        await create_plot(user_id=user_id,
                          lang=lang,
                          plot_type=callback.data,
                          sessionmaker=sessionmaker)

        await bot.send_photo(chat_id=callback.message.chat.id,
                             photo=FSInputFile(file_path))

        if os.path.exists(file_path):
            os.remove(file_path)

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        lang = await get_language(user_id=callback.from_user.id,
                                  sessionmaker=sessionmaker)
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
