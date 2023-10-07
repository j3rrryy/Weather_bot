from dataclasses import dataclass

from environs import Env


__all__ = ['Config', 'load_config']


@dataclass
class TgBot:
    token: str


@dataclass
class DatabaseConfig:
    driver: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    database: str


@dataclass
class RedisConfig:
    redis_host: str


@dataclass
class WeatherConfig:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: RedisConfig
    weather: WeatherConfig


def load_config() -> Config:
    """
    Create the bot config class.
    """

    env: Env = Env()
    env.read_env()

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  db=DatabaseConfig(driver=env('DB_DRIVER'),
                                    db_user=env('POSTGRES_USER'),
                                    db_password=env('POSTGRES_PASSWORD'),
                                    db_host=env('POSTGRES_HOST'),
                                    db_port=env('POSTGRES_PORT'),
                                    database=env('POSTGRES_DB')),
                  redis=RedisConfig(redis_host=env('REDIS_HOST')),
                  weather=WeatherConfig(token=env('WEATHER_API')))
