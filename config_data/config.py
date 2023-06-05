from dataclasses import dataclass

from environs import Env


__all__ = ['Config', 'load_config']


@dataclass
class TgBot:
    token: str

@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str

@dataclass
class RedisConfig:
    redis_host: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: RedisConfig


def load_config(path: str | None) -> Config:
    """
    Create the bot config class.
    """

    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  db=DatabaseConfig(database=env('DATABASE'),
                                    db_host='mysql',
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD')),
                  redis=RedisConfig(redis_host=env('REDIS_HOST')))
