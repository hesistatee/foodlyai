import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from database.database import database
from database.db_middleware import DBSessionMiddleware
from handlers import (
    count_calories,
    payment,
    product_composition,
    start,
    subscribe_status,
)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.update.middleware(DBSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(product_composition.router)
    dp.include_router(count_calories.router)
    dp.include_router(subscribe_status.router)
    dp.include_router(payment.router)

    logging.basicConfig(
        filename="logs.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        await database.init_db()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
