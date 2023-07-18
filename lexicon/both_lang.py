LEXICON_BOTH: dict[str, str] = {
    '/start': '<b>Hi!</b>\U0001f603\nI can show weather forecasts\u2728\
                \nTo continue you need to set your language\n\
                \n<b>Привет!</b>\U0001f603\
                \nЯ умею показывать прогноз погоды\u2728\
                \nДля продолжения тебе нужно установить свой язык',
    '/settings': 'First of all, you need to set your language\
                \nДля начала установим язык',
    'unknown': 'Sorry, unfortunately, I don\'t understand you.\
                \nIf you are setting up a bot, then follow the commands.\
                \nIf not, then use /help\n\
                \nИзвините, к сожалению, я вас не понимаю.\
                \nЕсли вы настраиваете бота, то следуйте командам.\
                \nЕсли нет, то используйте /help'
}

KB_LEXICON_BOTH: dict[str, str] = {
    'RU': 'Русский',
    'EN': 'English'
}

LEXICON_COMMANDS_BOTH: dict[str, str] = {
    '/weather': 'Weather forecast / Прогноз погоды',
    '/profile': 'Config / Конфигурация',
    '/settings': 'Settings / Настройки'
}

ERROR_LEXICON_BOTH: dict[str, str] = {
    'DataError': '<b>An error has occurred!\U0001f622</b>\
                    \nThere is a problem with the database. You can try to fix it if you are not at the stage of configuration of the bot by going through the setup procedure /settings.\
                    \nIf that did not help, then try again later\n\
                    \n<b>Произошла ошибка!</b>\U0001f622\
                    \nВозникла проблема с базой данных. Если вы не находитесь на стадии настройки бота, то вы можете попробовать пройти процедуру настройки /settings.\
                    \nЕсли это не помогло, то повторите попытку позже',
}
