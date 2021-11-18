from telethon import TelegramClient
import json

from session import Session

with open('configuration.json', 'r') as file:
    config = json.load(file)

api_id = config['api_id']
api_hash = config['api_hash']

client = TelegramClient('current', api_id, api_hash)


async def run_covert_channel():
    session = Session(client, 1, 2)
    await session.open()


with client:
    client.loop.run_until_complete(run_covert_channel())
