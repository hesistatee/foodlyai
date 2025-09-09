import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import start, product_composition, count_calories, subscribe_status, payment
from config import config
from database.db_middleware import DBSessionMiddleware
from database.database import database


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    dp.update.middleware(DBSessionMiddleware())
    
    dp.include_router(start.router)
    dp.include_router(product_composition.router)
    dp.include_router(count_calories.router)
    dp.include_router(subscribe_status.router)
    dp.include_router(payment.router)
    
    logging.basicConfig(
        filename='logs.log',
        level=logging.INFO, 
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        await database.init_db()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())