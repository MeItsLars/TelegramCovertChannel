from telethon import TelegramClient


class Session:

    def __init__(self, client: TelegramClient, my_id: int, other_id: int):
        self.client = client
        self.my_id = my_id
        self.other_id = other_id
        self.my_pack = StickerPack(client, str(my_id) + "_" + str(other_id))
        self.other_pack = StickerPack(client, str(other_id) + "_" + str(my_id))

    async def open(self):
        await self.my_pack.create()

    async def close(self):
        await self.my_pack.delete()


class StickerPack:
    PREFIX = "RU_TCC_"

    def __init__(self, client: TelegramClient, pack_id: str):
        self.client = client
        self.id = StickerPack.PREFIX + pack_id

    async def create(self):
        await self.client.send_message('@Stickers', '/newpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_file('@Stickers', './pack_image.png', force_document=True)
        await self.client.send_message('@Stickers', '😉')
        await self.client.send_message('@Stickers', '/publish')
        await self.client.send_message('@Stickers', '/skip')
        await self.client.send_message('@Stickers', self.id)

    async def delete(self):
        await self.client.send_message('@Stickers', '/delpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_message('@Stickers', 'Yes, I am totally sure.')
