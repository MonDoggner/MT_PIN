import asyncio
import logging

from aiogram import Dispatcher
from core.handlers import bot
from core.handlers import router

dp = Dispatcher()

async def main():    
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f'INFO:Выход')
