import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import start, product_composition
from config import config


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(start.router)
    dp.include_router(product_composition.router)
    
    logging.basicConfig(
        filename='logs.log',
        level=logging.INFO, 
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())