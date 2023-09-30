import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config_data import Config, load_config
from database import get_sessionmaker
from handlers import router as user_handlers_router
from keyboards import set_main_menu


logger = logging.getLogger(__name__)


async def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config(None)

    storage: RedisStorage = RedisStorage(
        redis=Redis(host=config.redis.redis_host))

    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    disp: Dispatcher = Dispatcher(storage=storage)

    await set_main_menu(bot)

    disp.include_router(user_handlers_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, sessionmaker=get_sessionmaker())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error('Bot stopped!')
        print(e)
