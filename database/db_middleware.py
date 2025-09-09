from .database import database
from aiogram import BaseMiddleware


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async for session in database.get_db():
            data['session'] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except:
                await session.rollback()
                raise
            finally:
                await session.close()