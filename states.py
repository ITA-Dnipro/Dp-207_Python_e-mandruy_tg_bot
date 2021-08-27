from aiogram.dispatcher.filters.state import StatesGroup, State

# state for weather
class Weather(StatesGroup):
    get_city = State()

# state for routes
class Route(StatesGroup):
    departure = State()
    arrival = State()
    date = State()
