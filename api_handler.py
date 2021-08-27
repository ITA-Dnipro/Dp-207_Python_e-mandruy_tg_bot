import aiohttp
import os


async def get_cities(message):
    async with aiohttp.ClientSession() as session:
        async with session.post(os.environ.get('API_CITIES'), json={'city': message}) as res:
            return await res.json()


async def get_routes(payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(os.environ.get('API_ROUTES_CARS'), json={'payload': payload}) as res:
            return await res.json()
