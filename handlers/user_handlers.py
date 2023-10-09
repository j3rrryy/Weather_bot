import os

from aiogram import Bot, Router, F
from aiogram.types import Message, ReplyKeyboardRemove,\
    CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

import services
import keyboards
from lexicon import LEXICON_BOTH, ERROR_LEXICON_BOTH
from middlewares import AntiFloodMiddleware
from states import FSMSettings, FSMLanguage
from database import post_lang, update_data
from errors import DataError, GetWeatherError


router: Router = Router()
router.message.middleware(AntiFloodMiddleware())


@router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext):
    """
    Send the start message and starts the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/start'], reply_markup=keyboards.language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['help']), StateFilter(default_state))
async def help_command(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the help messasge.
    """

    try:
        _, msg, _ = await services.create_message(user_id=message.from_user.id,
                                                  msg_type='/help',
                                                  sessionmaker=sessionmaker)
        await message.answer(msg)
    except DataError as error:
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.message(Command(commands=['settings']), StateFilter(default_state))
async def settings_command(message: Message, state: FSMContext):
    """
    Start the configuration procedure.
    """

    await message.answer(LEXICON_BOTH['/settings'], reply_markup=keyboards.language_kb())
    await state.set_state(FSMLanguage.set_language)


@router.message(Command(commands=['weather']), StateFilter(default_state))
async def weather_command(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a message which allows the user to choose the weather forecast mode.
    """

    try:
        lang, msg, _ = await services.create_message(user_id=message.from_user.id,
                                                     msg_type='/weather',
                                                     sessionmaker=sessionmaker)
        await message.answer(msg, reply_markup=keyboards.weather_kb(lang))

    except DataError as error:
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.message(Command(commands=['profile']), StateFilter(default_state))
async def get_profile(message: Message, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the user profile.
    """

    try:
        lang, msg, _ = await services.create_message(user_id=message.from_user.id,
                                                     msg_type='your_profile',
                                                     sessionmaker=sessionmaker)
        await message.answer(f'{msg}\n\n{await services.create_profile(user_id=message.from_user.id, lang=lang, sessionmaker=sessionmaker)}')

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
        lang, msg, _ = await services.create_message(user_id=callback.from_user.id,
                                                     msg_type='lang_success',
                                                     sessionmaker=sessionmaker)
        await callback.message.answer(msg, reply_markup=keyboards.location_kb(lang))

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
        _, msg, _ = await services.create_message(user_id=message.from_user.id,
                                                  msg_type='loc_success',
                                                  sessionmaker=sessionmaker)
        await message.answer(msg, reply_markup=keyboards.temp_kb())

    except DataError as error:
        await state.clear()
        print(error)
        await message.answer(ERROR_LEXICON_BOTH['DataError'])

    await state.set_state(FSMSettings.unit_of_temp)


@router.callback_query(StateFilter(FSMSettings.unit_of_temp),
                       F.data.in_(['celsius', 'fahrenheit']))
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
        lang, msg, _ = await services.create_message(user_id=callback.from_user.id,
                                                     msg_type='temp_success',
                                                     sessionmaker=sessionmaker)
        await callback.message.edit_text(msg, reply_markup=keyboards.wind_kb(lang))

    except DataError as error:
        await state.clear()
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    await state.set_state(FSMSettings.unit_of_wind)


@router.callback_query(StateFilter(FSMSettings.unit_of_wind),
                       F.data.in_(['mps', 'kmph']))
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
        _, msg, _ = await services.create_message(user_id=callback.from_user.id,
                                                  msg_type='settings_completed',
                                                  sessionmaker=sessionmaker)
        await callback.message.answer(msg, reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

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
                       F.data.in_(['forecast_today']))
async def get_forecast_today(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send weather forecast for today.
    """

    await callback.answer()

    try:
        lang, msg, error_msg = await services.create_message(user_id=callback.from_user.id,
                                                             msg_type='weather_today',
                                                             sessionmaker=sessionmaker)
        res: str = await services.create_forecast_today(user_id=callback.from_user.id,
                                                        lang=lang,
                                                        sessionmaker=sessionmaker)
        await callback.message.edit_text(f'{msg}{res}')

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        await callback.message.edit_text(error_msg)


@router.callback_query(StateFilter(default_state),
                       F.data.in_(['forecast_week', 'back_ds']))
async def week_forecast_days(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a message which allows the user to choose the weather forecast
    for a certain day or to choose the weather plots mode.
    """

    await callback.answer()

    lang, msg, _ = await services.create_message(user_id=callback.from_user.id,
                                                 msg_type='weather_week',
                                                 sessionmaker=sessionmaker)
    await callback.message.edit_text(msg, reply_markup=await keyboards.days_kb(user_id=callback.from_user.id,
                                                                               lang=lang,
                                                                               sessionmaker=sessionmaker))


@router.callback_query(StateFilter(default_state),
                       F.data.in_([str(day).zfill(2) for day in range(1, 32)]))
async def get_forecast_week(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send weather forecast for the following day.
    """

    await callback.answer()

    try:
        lang, _, error_msg = await services.create_message(user_id=callback.from_user.id,
                                                           sessionmaker=sessionmaker)
        res: dict[str, str] = await services.create_forecast_week(user_id=callback.from_user.id,
                                                                  lang=lang,
                                                                  sessionmaker=sessionmaker)
        await callback.message.edit_text(res[callback.data], reply_markup=keyboards.back_kb(lang, 'days'))

    except DataError as error:
        print(error)
        await callback.message.edit_text(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        await callback.message.edit_text(error_msg)


@router.callback_query(StateFilter(default_state),
                       F.data.in_(['plots', 'back_pl']))
async def get_plots(callback: CallbackQuery, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send the weather plots list.
    """

    await callback.answer()

    try:
        lang, msg, _ = await services.create_message(user_id=callback.from_user.id,
                                                     msg_type='plots',
                                                     sessionmaker=sessionmaker)
        await callback.message.answer(msg, reply_markup=keyboards.plots_kb(lang))

    except DataError as error:
        print(error)
        await callback.message.answer(ERROR_LEXICON_BOTH['DataError'])


@router.callback_query(StateFilter(default_state),
                       F.data.in_(['temp', 'wind', 'precip', 'humid']))
async def get_plot(callback: CallbackQuery, bot: Bot, sessionmaker: async_sessionmaker[AsyncSession]):
    """
    Send a weather plot.
    """

    await callback.answer()

    try:
        user_id = callback.from_user.id
        file_path = fr'./services/temp/{user_id}_plot.png'
        lang, _, error_msg = await services.create_message(user_id=callback.from_user.id,
                                                           sessionmaker=sessionmaker)

        await services.create_plot(user_id=user_id,
                                   lang=lang,
                                   plot_type=callback.data,
                                   sessionmaker=sessionmaker)

        await bot.send_photo(chat_id=callback.message.chat.id,
                             photo=FSInputFile(file_path),
                             reply_markup=keyboards.back_kb(lang, 'plots'))

        if os.path.exists(file_path):
            os.remove(file_path)

    except DataError as error:
        print(error)
        await callback.message.answer(ERROR_LEXICON_BOTH['DataError'])

    except GetWeatherError as error:
        print(error)
        await callback.message.answer(error_msg, reply_markup=keyboards.back_kb(lang, 'plots'))


@router.message()
async def unknown(message: Message):
    """
    Send a message that it can not understand the user.
    """

    await message.answer(LEXICON_BOTH['unknown'])
