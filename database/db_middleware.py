from collections.abc import Awaitable
from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from database.database import database
from database.repositories import UserRepository


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async for session in database.get_db():
            data["session"] = session

            if isinstance(event, Update):
                tg_id = None
                user = None
                if event.message and event.message.from_user:
                    tg_id = event.message.from_user.id
                elif event.callback_query:
                    tg_id = event.callback_query.from_user.id
                if tg_id:
                    user_repo = UserRepository(session=session)
                    user = await user_repo.get_user(telegram_id=tg_id)
                if user:
                    data["user"] = user
            return await handler(event, data)
