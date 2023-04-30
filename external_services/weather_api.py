from aiohttp import ClientSession
from environs import Env
from errors import GetWeatherError


env: Env = Env()
env.read_env(None)


async def get_weather(today: bool, **commands: str):
    """
    Gets weather info for today or for the following days.
    """

    params = '&'.join([f'{k}={v}' for k, v in commands.items()])

    if today:
        # get weather forecast for today
        url = f'http://api.weatherapi.com/v1/current.json?key={env("WEATHER_API")}&{params}'
    else:
        # get weather forecast for the following days
        url = f'http://api.weatherapi.com/v1/forecast.json?key={env("WEATHER_API")}&{params}'

    async with ClientSession() as session:
        async with session.get(url) as resp:
            res = await resp.json(encoding='utf-8')

    if 'error' in res.keys():
        raise GetWeatherError
    return res
