import os
import shutil
from stegano import lsb

from telethon import TelegramClient
from telethon.tl.functions.messages import GetAllStickersRequest, InstallStickerSetRequest, GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, InputStickerSetID

from covertchannel.steganography import encode_in_images, decode_image


class Channel:

    def __init__(self, client_id: str, api_id: int, api_hash: str, other_client_id: str):
        # Create client and client IDs
        self.client_id = client_id
        self.other_client_id = other_client_id
        self.client = TelegramClient(client_id, api_id, api_hash)
        # Create sticker packs
        self.my_pack = StickerPack(self.client, self.client_id + "_" + self.other_client_id)
        self.other_pack = StickerPack(self.client, self.other_client_id + "_" + self.client_id)

    def initialize(self):
        # Initialize channel
        print('[Client "' + self.client_id + '"] Initializing channel...')
        self.client.start()

        # Create the sticker pack for the communication
        print('[Client "' + self.client_id + '"] Creating sticker pack...')
        self.client.loop.run_until_complete(self.my_pack.create())

        # Subscribe to our own sticker pack so we can access it
        print('[Client "' + self.client_id + '"] Subscribing to own sticker pack...')
        self.client.loop.run_until_complete(
            self.client(InstallStickerSetRequest(InputStickerSetShortName(self.my_pack.id), False)))

        # Subscribe to the other sticker pack so we can read it
        # TODO: Uncomment
        # print('[Client "' + self.client_id + '"] Subscribing to other sticker pack...')
        # attempt = 0
        # while True:
        #     try:
        #         print('[Client "' + self.client_id + '"] Attempt ' + str(attempt) + '...')
        #         self.client.loop.run_until_complete(
        #             self.client(InstallStickerSetRequest(InputStickerSetShortName(self.other_pack.id), False)))
        #         print('[Client "' + self.client_id + '"] Initialized channel!')
        #         return
        #     except StickersetInvalidError:
        #         attempt += 1
        #         time.sleep(5)

    def send_str(self, data: str):
        self.send(bytes(data, 'ascii'))

    async def download(self, sticker, file):
        await self.client.download_media(sticker, file=file)

    def send(self, data: bytes):
        self.client.loop.run_until_complete(self.my_pack.clear())
        path = os.path.join('./', 'message_sticker_files/')
        os.mkdir(path)
        encode_in_images(path + '1.webp', data)
        self.client.loop.run_until_complete(self.my_pack.add_from_directory(path))

        self.client.loop.run_until_complete(self.my_pack.refresh())
        self.client.loop.run_until_complete(self.download(self.my_pack.stickers.documents[1], 'test'))
        print(decode_image('test.webp'))
        shutil.rmtree(path)

    def close(self):
        print('[Client "' + self.client_id + '"] Closing channel...')
        self.client.loop.run_until_complete(self.my_pack.delete())
        print('[Client "' + self.client_id + '"] Session closed!')


class StickerPack:
    URL_PREFIX = "https://t.me/addstickers/"
    PREFIX = "RU_TCC_"

    def __init__(self, client: TelegramClient, pack_id: str):
        self.client = client
        self.id = StickerPack.PREFIX + pack_id
        self.stickers = None

    async def create(self):
        await self.client.send_message('@Stickers', '/newpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_file('@Stickers',
                                    file=os.path.join(os.path.dirname(__file__), 'resources/pack_image.png'),
                                    force_document=True)
        await self.client.send_message('@Stickers', '😀')
        await self.client.send_file('@Stickers',
                                    file=os.path.join(os.path.dirname(__file__), 'resources/pack_image.png'),
                                    force_document=True)
        await self.client.send_message('@Stickers', '😃')
        await self.client.send_message('@Stickers', '/publish')
        await self.client.send_message('@Stickers', '/skip')
        await self.client.send_message('@Stickers', self.id)

    async def refresh(self):
        # Load all installed sticker packs and fetch this pack
        result_sticker_set = None
        sticker_sets = await self.client(GetAllStickersRequest(0))
        for sticker_set in sticker_sets.sets:
            if sticker_set.title == self.id:
                result_sticker_set = sticker_set
                break

        # Load all stickers in the newly fetched sticker pack
        self.stickers = await self.client(GetStickerSetRequest(
            stickerset=InputStickerSetID(
                id=result_sticker_set.id, access_hash=result_sticker_set.access_hash
            )
        ))

    async def clear(self):
        # Refresh the sticker pack
        await self.refresh()
        # Delete all stickers except the initial one
        for i in range(1, len(self.stickers.documents)):
            await self.client.send_message('@Stickers', '/delsticker')
            await self.client.send_file('@Stickers', self.stickers.documents[i])
        # We need to wait for the pack to update (waiting for the Stickers bot to respond)
        await self.client.send_message('@Stickers', '/cancel')
        # Refresh the sticker pack again
        await self.refresh()

    async def add_from_directory(self, path):
        await self.client.send_message('@Stickers', '/addsticker')
        for sticker in os.listdir(path):
            await self.client.send_message('@Stickers', self.id)
            await self.client.send_file('@Stickers',
                                        file=os.path.join(path, sticker),
                                        force_document=True)
            await self.client.send_message('@Stickers', '😃')
        await self.client.send_message('@Stickers', '/done')

    async def delete(self):
        await self.client.send_message('@Stickers', '/delpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_message('@Stickers', 'Yes, I am totally sure.')

    def get_url(self) -> str:
        return StickerPack.URL_PREFIX + self.id
