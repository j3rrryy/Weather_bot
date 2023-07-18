from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import matplotlib.pyplot as plt
import pytz
import timezonefinder

from external_services import get_weather
from database import get_data
from lexicon import KB_LEXICON_RU, KB_LEXICON_EN


WIND_DIR_RU: dict[str, str] = {
    'N': 'С',
    'NNE': 'ССВ',
    'NE': 'СВ',
    'ENE': 'ВСВ',
    'E': 'В',
    'ESE': 'ВЮВ',
    'SE': 'ЮВ',
    'SSE': 'ЮЮВ',
    'S': 'Ю',
    'SSW': 'ЮЮЗ',
    'SW': 'ЮЗ',
    'WSW': 'ЗЮЗ',
    'W': 'З',
    'WNW': 'ЗСЗ',
    'NW': 'СЗ',
    'NNW': 'ССЗ'
}


async def days_generator(user_id: int, sessionmaker: async_sessionmaker[AsyncSession]) -> tuple:
    """
    Get 3 days using tz.
    """

    user_info: dict[str, str | float] = await get_data(
        user_id=user_id, sessionmaker=sessionmaker)

    tf = timezonefinder.TimezoneFinder()
    dt = datetime.utcnow()

    timezone_str = tf.certain_timezone_at(
        lat=float(user_info["latitude"]), lng=float(user_info["longitude"]))

    if timezone_str is None:
        return tuple((dt + timedelta(days=i)).strftime('%d') for i in range(3))
    else:
        timezone = pytz.timezone(timezone_str)
        return tuple((dt + timezone.utcoffset(dt) + timedelta(days=i)).strftime('%d') for i in range(3))


async def create_forecast_today(user_id: int,
                                lang: str,
                                sessionmaker: async_sessionmaker[AsyncSession]) -> str:
    """
    Create weather forecast for today.
    """

    user_info: dict[str, str | float] = await get_data(
        user_id=user_id, sessionmaker=sessionmaker)

    if lang == 'RU':
        weather_info = await get_weather(True,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         aqi='no',
                                         lang='ru')
    else:
        weather_info = await get_weather(True,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         aqi='no',
                                         lang='en')

    condition: str = str(weather_info['current']['condition']['text'])

    if user_info['temp_unit'] == 'celsius':
        temp: str = str(weather_info['current']['temp_c'])
        feelslike_t: str = str(weather_info['current']['feelslike_c'])
    else:
        temp: str = str(weather_info['current']['temp_f'])
        feelslike_t: str = str(weather_info['current']['feelslike_f'])

    if user_info['wind_unit'] == 'kmph':
        if lang == 'RU':
            wind_speed: str = f'{weather_info["current"]["wind_kph"]} км/ч'
        else:
            wind_speed: str = f'{weather_info["current"]["wind_kph"]} km/h'
    else:
        if lang == 'RU':
            wind_speed: str = f'{int(weather_info["current"]["wind_kph"]) // 3.6} м/с'
        else:
            wind_speed: str = f'{int(weather_info["current"]["wind_kph"]) // 3.6} m/s'

    if lang == 'RU':
        wind_degree: str = WIND_DIR_RU[weather_info['current']['wind_dir']]
    else:
        wind_degree: str = weather_info['current']['wind_dir']

    pressure: str = str(
        round(int(weather_info['current']['pressure_mb']) * 0.750064))

    if int(weather_info['current']['precip_mm']) == 0:
        if lang == 'RU':
            precip: str = 'не ожидаются'
        else:
            precip: str = 'not expected'
    else:
        if lang == 'RU':
            precip: str = f'{weather_info["current"]["precip_mm"]} мм'
        else:
            precip: str = f'{weather_info["current"]["precip_mm"]} mm'

    humidity: str = str(weather_info['current']['humidity'])
    cloud: str = str(weather_info['current']['cloud'])

    if lang == 'RU':
        res = f'{condition.capitalize()}\n\
                \nТемпература воздуха: {temp}\u00b0,\
                \nощущается как: {feelslike_t}\u00b0\n\
                \nНаправление ветра: {wind_degree},\
                \nскорость ветра: {wind_speed}\n\
                \nДавление воздуха: {pressure} мм рт.ст.\n\
                \nОсадки: {precip}\n\
                \nВлажность: {humidity}%\n\
                \nОблачность: {cloud}%'
    else:
        res = f'{condition.capitalize()}\n\
                \nAir temperature: {temp}\u00b0,\
                \nfeels like: {feelslike_t}\u00b0\n\
                \nWind direction: {wind_degree},\
                \nwind speed: {wind_speed}\n\
                \nAir pressure: {pressure} mmHg\n\
                \nPrecipitation: {precip}\n\
                \nHumidity: {humidity}%\n\
                \nCloud cover: {cloud}%'

    return res


async def create_forecast_week(user_id: int, lang: str, sessionmaker: async_sessionmaker[AsyncSession]) -> dict[str, str]:
    """
    Create weather forecast for the following days.
    """

    user_info: dict[str, str | float] = await get_data(
        user_id=user_id, sessionmaker=sessionmaker)

    if lang == 'RU':
        weather_info = await get_weather(False,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         days='3',
                                         aqi='no',
                                         alerts='no',
                                         lang='ru')
    else:
        weather_info = await get_weather(False,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         days='3',
                                         aqi='no',
                                         alerts='no',
                                         lang='en')

    res = {}

    for day in weather_info['forecast']['forecastday']:

        day_n: str = str(day['date'][-2:])
        condition = str(day['day']['condition']['text'])

        if user_info['temp_unit'] == 'celsius':
            maxtemp = str(day['day']['maxtemp_c'])
            mintemp = str(day['day']['mintemp_c'])
            avgtemp = str(day['day']['avgtemp_c'])
        else:
            maxtemp = str(day['day']['maxtemp_f'])
            mintemp = str(day['day']['mintemp_f'])
            avgtemp = str(day['day']['avgtemp_f'])

        if user_info['wind_unit'] == 'kmph':
            if lang == 'RU':
                maxwind = f'{day["day"]["maxwind_kph"]} км/ч'
            else:
                maxwind = f'{day["day"]["maxwind_kph"]} km/h'
        else:
            if lang == 'RU':
                maxwind = f'{int(day["day"]["maxwind_kph"]) // 3.6} м/с'
            else:
                maxwind = f'{int(day["day"]["maxwind_kph"]) // 3.6} m/s'

        if int(day['day']['totalprecip_mm']) == 0:
            if lang == 'RU':
                totalprecip = 'не ожидаются'
            else:
                totalprecip = 'not expected'
        else:
            if lang == 'RU':
                totalprecip = f'{day["day"]["totalprecip_mm"]} мм'
            else:
                totalprecip = f'{day["day"]["totalprecip_mm"]} mm'

        avghumidity = str(day['day']['avghumidity'])

        if lang == 'RU':
            info = f'{condition.capitalize()}\n\
                    \nСредняя температура воздуха: {avgtemp}\u00b0,\
                    \nмаксимальная: {maxtemp}\u00b0,\nминимальная: {mintemp}\u00b0\n\
                    \nМаксимальная скорость ветра: {maxwind}\n\
                    \nОсадки: {totalprecip}\n\
                    \nСредняя влажность воздуха: {avghumidity}%'
        else:
            info = f'{condition.capitalize()}\n\
                    \nAverage air temperature: {avgtemp}\u00b0,\
                    \nmaximum: {maxtemp}\u00b0,\nminimum: {mintemp}\u00b0\n\
                    \nMaximum wind speed: {maxwind}\n\
                    \nPrecipitation: {totalprecip}\n\
                    \nAverage air humidity: {avghumidity}%'

        res.setdefault(day_n, info)

    return res


async def create_profile(user_id: int, lang: str, sessionmaker: async_sessionmaker[AsyncSession]) -> str:
    """
    Create user profile.
    """

    user_info: dict[str, str | float] = (await get_data(user_id=user_id, sessionmaker=sessionmaker))

    if lang == 'RU':
        return f'Язык: {user_info["language"]}\
                \nШирота: {float(user_info["latitude"])}\
                \nДолгота: {float(user_info["longitude"])}\
                \nЕдиницы измерения температуры: {KB_LEXICON_RU[user_info["temp_unit"]]}\
                \nЕдиницы измерения скорости ветра: {KB_LEXICON_RU[user_info["wind_unit"]]}'
    else:
        return f'Language: {user_info["language"]}\
                \nLatitude: {float(user_info["latitude"])}\
                \nLongitude: {float(user_info["longitude"])}\
                \nTemperature measurement units: {KB_LEXICON_EN[user_info["temp_unit"]]}\
                \nUnits of wind speed measurement: {KB_LEXICON_EN[user_info["wind_unit"]]}'


async def create_plot(user_id: int,
                      lang: str,
                      plot_type: str,
                      sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    """
    Create different weather plots.
    """

    user_info: dict[str, str | float] = await get_data(user_id=user_id, sessionmaker=sessionmaker)

    if lang == 'RU':
        weather_info = await get_weather(False,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         days='3',
                                         aqi='no',
                                         alerts='no',
                                         lang='ru')
    else:
        weather_info = await get_weather(False,
                                         q=f'{float(user_info["latitude"])},{float(user_info["longitude"])}',
                                         days='3',
                                         aqi='no',
                                         alerts='no',
                                         lang='en')

    x = tuple(await days_generator(user_id=user_id, sessionmaker=sessionmaker))
    y = []

    if lang == 'RU':
        plt.xlabel('Дни')
    else:
        plt.xlabel('Days')

    match plot_type:

        # temperature plot
        case 'temp':
            for day in weather_info['forecast']['forecastday']:
                if user_info['temp_unit'] == 'celsius':
                    y.append(int(day['day']['avgtemp_c']))
                else:
                    y.append(int(day['day']['avgtemp_f']))

            if lang == 'RU':
                plt.ylabel(
                    f'Температура, {KB_LEXICON_RU[user_info["temp_unit"]]}')
                plt.title('График температуры')
            else:
                plt.ylabel(
                    f'Temperature, {KB_LEXICON_EN[user_info["temp_unit"]]}')
                plt.title('Temperature plot')

        # wind speed plot
        case 'wind':
            for day in weather_info['forecast']['forecastday']:
                if user_info['wind_unit'] == 'kmph':
                    y.append(int(day["day"]["maxwind_kph"]))
                else:
                    y.append(int(day["day"]["maxwind_kph"]) // 3.6)

            if lang == 'RU':
                plt.ylabel(
                    f'Скорость ветра, {KB_LEXICON_RU[user_info["wind_unit"]]}')
                plt.title('График скорости ветра')
            else:
                plt.ylabel(
                    f'Wind speed, {KB_LEXICON_EN[user_info["wind_unit"]]}')
                plt.title('Wind speed plot')

        # precipation plot
        case 'precip':
            for day in weather_info['forecast']['forecastday']:
                y.append(int(day["day"]["totalprecip_mm"]))

            if lang == 'RU':
                plt.ylabel('Осадки, мм')
                plt.title('График осадков')
            else:
                plt.ylabel('Precipitation, mm')
                plt.title('Precipitation plot')

        # humidity plot
        case 'humid':
            for day in weather_info['forecast']['forecastday']:
                y.append(int(day['day']['avghumidity']))

            if lang == 'RU':
                plt.ylabel('Влажность, %')
                plt.title('График влажности')
            else:
                plt.ylabel('Humidity, %')
                plt.title('Humidity plot')

    plt.plot(x, y, color='blue', marker='o',
             markersize=6, markerfacecolor='black')

    plt.savefig(f'./services/{str(user_id)}_plot.png')
    plt.close()
