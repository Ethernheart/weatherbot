import main
from aiogram import Bot, Dispatcher, types
from aiogram.types import *
from aiogram.utils import executor
from config import tg_bot_token as bt
from base import Database
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

db = Database('database.db')
bot = Bot(bt)
dp = Dispatcher(bot)


async def autoSend():
    data = main.get_weather('Ростов')
    users = db.get_user()
    for u in users:
        await bot.send_message(u[0], data)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    print(datetime.datetime.utcnow().hour)
    print(datetime.datetime.utcnow().minute)
    scheduler.add_job(autoSend, trigger='interval', seconds=5 )
    scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
