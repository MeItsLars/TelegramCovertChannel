import asyncio

from telethon.tl.functions.messages import GetAllStickersRequest
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from telethon.tl.functions.messages import GetAllStickersRequest

async def doezooi():
    api_id = 8205533
    api_hash = 'e0750e29f8b159ac273dc072e0541e67'

    client = TelegramClient('current', api_id, api_hash)
    client.start()
    await client.connect()

    # Get all the sticker sets this user has
    sticker_sets = await client(GetAllStickersRequest(0))

    print(sticker_sets)

    # Choose a sticker set
    sticker_set = sticker_sets.sets[0]

    print('=======================')
    print(sticker_set.id)

    # Get the stickers for this sticker set
    stickers = await client(GetStickerSetRequest(
        stickerset=InputStickerSetID(
            id=sticker_set.id, access_hash=sticker_set.access_hash
        )
    ))

    print(stickers)
    print(stickers.documents[0])

    await client.download_media(stickers.documents[0], "sticker.png")

    print('Done!')

    await client.disconnect()

asyncio.run(doezooi())
