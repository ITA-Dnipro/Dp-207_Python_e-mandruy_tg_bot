from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


btn_main = KeyboardButton('main')


# main menu buttons
btn_transport = KeyboardButton('transport')
btn_weather = KeyboardButton('weather')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_transport, btn_weather)
