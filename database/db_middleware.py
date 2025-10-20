from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Any
from collections.abc import Awaitable
from database.database import database


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async for session in database.get_db():
            data["session"] = session
            return await handler(event, data)
