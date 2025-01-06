from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.lexicon import KB_LEXICON_BOTH, KB_LEXICON_EN, KB_LEXICON_RU
from src.services import days_generator


def language_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to select a language.
    """

    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(text=KB_LEXICON_BOTH["RU"], callback_data="RU"),
        InlineKeyboardButton(text=KB_LEXICON_BOTH["EN"], callback_data="EN"),
    )
    return kb_builder.as_markup()


def location_kb(lang: str) -> ReplyKeyboardMarkup:
    """
    Build a keyboard which allows the user to set his location.
    """

    kb_builder = ReplyKeyboardBuilder()

    if lang == "RU":
        kb_builder.add(
            KeyboardButton(text=KB_LEXICON_RU["get_location"], request_location=True)
        )
    else:
        kb_builder.add(
            KeyboardButton(text=KB_LEXICON_EN["get_location"], request_location=True)
        )
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def temp_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to select temperature measurement units.
    """

    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(text=KB_LEXICON_RU["celsius"], callback_data="celsius"),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["fahrenheit"], callback_data="fahrenheit"
        ),
    )
    return kb_builder.as_markup()


def wind_kb(lang: str) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to select wind speed measurement units.
    """

    kb_builder = InlineKeyboardBuilder()

    if lang == "RU":
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_RU["mps"], callback_data="mps"),
            InlineKeyboardButton(text=KB_LEXICON_RU["kmph"], callback_data="kmph"),
        )
    else:
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_EN["mps"], callback_data="mps"),
            InlineKeyboardButton(text=KB_LEXICON_EN["kmph"], callback_data="kmph"),
        )
    return kb_builder.as_markup()


def weather_kb(lang: str) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to choose the weather forecast mode.
    """

    kb_builder = InlineKeyboardBuilder()

    if lang == "RU":
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["today"], callback_data="forecast_today"
            ),
            InlineKeyboardButton(
                text=KB_LEXICON_RU["week"], callback_data="forecast_week"
            ),
            width=1,
        )
    else:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_EN["today"], callback_data="forecast_today"
            ),
            InlineKeyboardButton(
                text=KB_LEXICON_EN["week"], callback_data="forecast_week"
            ),
            width=1,
        )
    return kb_builder.as_markup()


async def days_kb(
    user_id: int, lang: str, sessionmaker: async_sessionmaker[AsyncSession]
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to choose the weather forecast for a certain day
    or to choose the weather plots mode.
    """

    kb_builder = InlineKeyboardBuilder()

    days = await days_generator(user_id=user_id, sessionmaker=sessionmaker)

    kb_builder.row(
        *(InlineKeyboardButton(text=s, callback_data=s) for s in days), width=4
    )

    if lang == "RU":
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_RU["plots"], callback_data="plots")
        )
    else:
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_EN["plots"], callback_data="plots")
        )
    return kb_builder.as_markup()


def plots_kb(lang: str) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to choose the certain weather plot.
    """

    kb_builder = InlineKeyboardBuilder()

    if lang == "RU":
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_RU["temp"], callback_data="temp"),
            InlineKeyboardButton(text=KB_LEXICON_RU["wind"], callback_data="wind"),
            InlineKeyboardButton(text=KB_LEXICON_RU["precip"], callback_data="precip"),
            InlineKeyboardButton(text=KB_LEXICON_RU["humid"], callback_data="humid"),
            InlineKeyboardButton(text=KB_LEXICON_RU["back"], callback_data="back_ds"),
            width=1,
        )
    else:
        kb_builder.row(
            InlineKeyboardButton(text=KB_LEXICON_EN["temp"], callback_data="temp"),
            InlineKeyboardButton(text=KB_LEXICON_EN["wind"], callback_data="wind"),
            InlineKeyboardButton(text=KB_LEXICON_EN["precip"], callback_data="precip"),
            InlineKeyboardButton(text=KB_LEXICON_EN["humid"], callback_data="humid"),
            InlineKeyboardButton(text=KB_LEXICON_EN["back"], callback_data="back_ds"),
            width=1,
        )
    return kb_builder.as_markup()


def back_kb(lang: str, to: str) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the menu.
    """

    kb_builder = InlineKeyboardBuilder()

    if lang == "RU":
        if to == "days":
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back"], callback_data="back_ds"
                )
            )
        elif to == "plots":
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back"], callback_data="back_pl"
                )
            )
    else:
        if to == "days":
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_EN["back"], callback_data="back_ds"
                )
            )
        elif to == "plots":
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_EN["back"], callback_data="back_pl"
                )
            )
    return kb_builder.as_markup()
