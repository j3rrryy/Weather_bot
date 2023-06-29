import datetime
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

class AntiFloodMiddleware(BaseMiddleware):
    """
    Antiflood protection
    """

    time_updates: dict[int, datetime.datetime] = {}
    timedelta_limiter: datetime.timedelta = datetime.timedelta(seconds=3)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            if user_id in self.time_updates.keys():
                if (datetime.datetime.now() - self.time_updates[user_id]) > self.timedelta_limiter:
                    self.time_updates[user_id] = datetime.datetime.now()
                    return await handler(event, data)
            else:
                self.time_updates[user_id] = datetime.datetime.now()
                return await handler(event, data)
