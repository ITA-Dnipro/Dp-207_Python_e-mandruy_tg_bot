import os
import sys
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import link
import emoji
from dotenv import load_dotenv
import markup as btn
from states import Weather, Route
from api_handler import get_cities, get_routes


load_dotenv()


API_TOKEN = os.getenv('BOT_TOKEN')


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# main handler
@dp.message_handler()
async def main_handler(message: types.Message):
    if message.text == 'weather':
        await enter_weather(message)
    elif message.text == 'transport':
        await enter_transport(message)
    elif message.text == '/start':
        await send_welcome(message)
    else:
        await message.answer('WRONG')


# welcome handler
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.message):
    await bot.send_message(message.from_user.id, f'Hello, {message.from_user.first_name}', reply_markup=btn.main_menu)


# weather handler for set state and get city
@dp.message_handler(state=None)
async def enter_weather(message: types.Message):
    await message.answer('Напишите город, пожалуйста')
    await Weather.get_city.set()


# weather handler with call to api for weather data
@dp.message_handler(state=Weather.get_city)
async def answer_get_city(message: types.Message, state: FSMContext):
    data = await get_cities(message.text)
    if 'msg' in data:
        await message.answer(data['msg'])
        await state.finish()
    await message.answer(f'Температура: {data["temperature"]}')
    await state.finish()


# transport handler for set state and
@dp.message_handler(state=None)
async def enter_transport(message: types.Message):
    await message.answer('Напишите город отправки, пожалуйста')
    await Route.departure.set()


# transport handler to switch to another state
@dp.message_handler(state=Route.departure)
async def answer_departure(message: types.Message, state: FSMContext):
    departure = message.text
    await state.update_data({'departure': departure})
    await message.answer('Напишите город прибытия, пожалуйста')
    await Route.arrival.set()


# transport handler to switch to another state
@dp.message_handler(state=Route.arrival)
async def answer_arrival(message: types.Message, state: FSMContext):
    arrival = message.text
    await state.update_data({'arrival': arrival})
    await message.answer('Напишите дату в формате дд.мм.гггг., пожалуйста')
    await Route.date.set()


# transport handler with call to api to get transport data
@dp.message_handler(state=Route.date)
async def answer_date(message: types.Message, state: FSMContext):
    date = message.text
    await state.update_data({'date': date})
    data = await state.get_data()
    payload = {"departure_name": data["departure"].capitalize(),
               "departure_date": data["date"],
               "arrival_name": data["arrival"].capitalize(),
               "transport_types": ["car"]}
    response = await get_routes(payload)
    await message.answer(data["date"])
    if response['cars_data']['trips']:
        for car in response['cars_data']['trips']:
            if car["car_model"]:
                await message.answer(f'{car["departure_name"]}-{car["arrival_name"]}\n'
                                     f'{car["car_model"]}\n'
                                     f'{car["price"]}\n'
                                     f'{link("Сылка на профиль", car["blablacar_url"])}\n'
                                     f'{emoji.emojize(":taxi:") * 20}\n', parse_mode='Markdown')
    else:
        await message.answer('к сожалению нет машин на эту дату')
    await state.finish()


if __name__ == '__main__':
    if API_TOKEN == 'NOT_A_TOKEN':
        sys.exit()
    executor.start_polling(dp, skip_updates=True)
