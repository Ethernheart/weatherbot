import requests
from datetime import datetime
from aiogram import Bot, types, Dispatcher, executor
from config import tg_bot_token as tt, open_weather_token as wt
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from base import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pprint


class CityState(StatesGroup):
    city = State()


storage = MemoryStorage()
bot = Bot(token=tt)
dp = Dispatcher(bot, storage=storage)
db = Database('database.db')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.answer('Здравствуй')


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    if message.chat.type == 'private':
        await message.answer(f'Команды: \n'
                             f'/start\n'
                             f'/setcity + Город')


async def autoSend():
    users = db.get_user()
    for u in users:
        data = get_weather(db.cursor.execute(f"SELECT City FROM users WHERE UserId = {u[0]}").fetchone()[0])
        await bot.send_message(u[0], data)


@dp.message_handler(commands=['setcity'])
async def set_city(message: types.Message):
    if message.chat.type == 'private':
        text = message.text[9:]
        db.set_city(text, message.from_user.id)
        await message.answer('Город добавлен успешно')


def get_weather(city):
    r = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?lang=ru&q={city}&units=metric&appid={wt}')
    answer = r.json()
    pprint.pprint(answer)
    sr = int(answer["sys"]['sunrise']) + 10800
    ss = int(answer["sys"]["sunset"]) + 10800
    data = dict(country_code=str(answer['sys']['country']),
                cor=str(answer["coord"]["lon"]) + " " + str(answer["coord"]["lat"]),
                sunrise=str(datetime.utcfromtimestamp(sr).strftime('%Y-%m-%d %H:%M:%S')),
                sunset=str(datetime.utcfromtimestamp(ss).strftime('%Y-%m-%d %H:%M:%S')),
                temp=str(answer["main"]['temp']), feels_like=str(answer["main"]['feels_like']),
                pressure=str(answer['main']["pressure"]), humidity=str(answer['main']['humidity']),
                main=str(answer["weather"][0]['main']), description=str(answer["weather"][0]['description']),
                speed=str(answer['wind']['speed']), deg=answer['wind']['deg'], city=answer['name'])
    country_code = data['country_code']
    cor = data['cor']
    sunrise = data['sunrise']
    sunset = data['sunset']
    temp = data['temp']
    feels_like = data['feels_like']
    pressure = data['pressure']
    humidity = data['humidity']
    description = data['description']
    speed = data['speed']
    city = data['city']
    degree_wind = data["deg"]

    if degree_wind < 15 or degree_wind > 345:
        degree_wind = "С"
    elif 15 < degree_wind < 75:
        degree_wind = "С/В"
    elif 75 < degree_wind < 105:
        degree_wind = "В"
    elif 105 < degree_wind < 165:
        degree_wind = "Ю/В"
    elif 165 < degree_wind < 195:
        degree_wind = "Ю"
    elif 195 < degree_wind < 225:
        degree_wind = "Ю/З"
    elif 255 < degree_wind < 285:
        degree_wind = "З"
    elif 285 < degree_wind < 345:
        degree_wind = "С/З"

    return (
        f"Код страны: {country_code}\n"
        f"Координаты города: {cor}\n"
        f"Восход: {sunrise}\n"
        f"Закат: {sunset}\n"
        f"Температура: {temp}C°\n"
        f"Ощущается как: {feels_like}\n"
        f"Давление: {pressure}\n"
        f"Влажность: {humidity}%\n"
        f"Погода: {description}\n"
        f"Скорость ветра: {speed}м/с,Направление ветра: {degree_wind}\n"
        f"название города: {city}")


scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
print(datetime.utcnow().hour)
print(datetime.utcnow().minute)
scheduler.add_job(autoSend, trigger='cron', hour=7,minute=0)
scheduler.start()
#  trigger='cron', hour=7,minute=0
# trigger='interval', seconds=5

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
