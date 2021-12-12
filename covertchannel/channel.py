import os
import shutil
import time

from telethon import TelegramClient
from telethon.errors import StickersetInvalidError
from telethon.tl.functions.messages import GetAllStickersRequest, InstallStickerSetRequest, GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, InputStickerSetID

from covertchannel.steganography import encode_sticker, decode_image


class Channel:
    """
    Represents a communication channel between two parties

    Attributes:
        client_id: String representing the ID of this client
        api_id: Integer representing the api ID, used for contacting the Telegram API
        api_hash: Used for contacting the Telegram API
        other_client_id: String representing the ID of the (other) client we're communicating with

    Methods:
        initialize: Initializes and starts the communication channel
        download: Downloads media from Telegram
        send: Converts the input to binary data, encodes it in stickers, and updates the sticker pack
        receive: Halting method that waits until the other client has sent new data, then returns this data
        close: Closes the communication channel with the other client
    """

    def __init__(self, client_id: str, api_id: int, api_hash: str, other_client_id: str):
        """
        Constructs the channel
        :param client_id: The ID of this client
        :param api_id: Used for contacting the Telegram API
        :param api_hash: Used for contacting the Telegram API
        :param other_client_id: The ID of the (other) client we're communicating with
        """
        # Create client and client IDs
        self.client_id = client_id
        self.other_client_id = other_client_id
        self.client = TelegramClient(client_id, api_id, api_hash)
        # Create sticker packs
        self.my_pack = StickerPack(self.client, self.client_id + "_" + self.other_client_id)
        self.other_pack = StickerPack(self.client, self.other_client_id + "_" + self.client_id)
        # Set message constants
        self.sequence_number = 0

    def initialize(self):
        """
        Initializes this channel by creating a sticker pack and subscribing to the other clients' sticker pack
        :return: Nothing
        """
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
        print('[Client "' + self.client_id + '"] Subscribing to other sticker pack...')
        attempt = 1
        while True:
            try:
                print('[Client "' + self.client_id + '"] Attempt ' + str(attempt) + '...')
                self.client.loop.run_until_complete(
                    self.client(InstallStickerSetRequest(InputStickerSetShortName(self.other_pack.id), False)))
                print('[Client "' + self.client_id + '"] Initialized channel!')
                return
            except StickersetInvalidError:
                attempt += 1
                time.sleep(5)

    async def download(self, sticker, file):
        """
        Downloads a sticker from Telegram and saves it to a file
        :param sticker: The sticker we want to download
        :param file: The file we want to store the sticker in
        :return: Nothing
        """
        await self.client.download_media(sticker, file=file)

    def send(self, data: bytes):
        """
        Sends the given data to the other client using encoding in stickers
        :param data: The data we want to send
        :return: Nothing
        """
        # Clear the current pack
        self.client.loop.run_until_complete(self.my_pack.clear())

        # Create a directory for the stickers
        path = os.path.join('./', 'message_sticker_files/')
        os.mkdir(path)

        # Construct the data
        block_size = 32768  # = 512 * 512 // 8
        no_of_stickers = ((4 + len(data)) + block_size - 1) // block_size
        data = self.sequence_number.to_bytes(3, 'big') + no_of_stickers.to_bytes(1, 'big') + data

        # Encode the data into stickers
        for i, block_start in enumerate(range(0, len(data), block_size)):
            block = data[block_start:block_start + block_size]
            encode_sticker(os.path.join(path, f'{i + 1000}.webp'), block)

        # Transmit the data
        self.client.loop.run_until_complete(self.my_pack.add_from_directory(path))

        # Delete the directory with the stickers
        shutil.rmtree(path)

    def receive(self):
        """
        Halting method that waits until the other client has sent new data, then returns it
        :return: None if the other client closed the communication, the data if it sent new data
        """
        path = os.path.join('./', 'message_sticker_files/')
        os.mkdir(path)
        while True:
            # Fetch the sticker pack. Return 'None' if the sticker pack no longer exists
            try:
                self.client.loop.run_until_complete(self.other_pack.refresh())
            except:
                shutil.rmtree(path)
                return None

            # Check if the sticker pack actually contains data
            if len(self.other_pack.stickers.documents) > 1:
                self.client.loop.run_until_complete(self.download(
                    self.other_pack.stickers.documents[1], './message_sticker_files/1'))

                # Decode the first sticker of the received sticker pack
                content = decode_image('./message_sticker_files/1.webp')
                received_sequence_number = int.from_bytes(content[:3], 'big')
                received_no_of_stickers = int.from_bytes(content[3:4], 'big')

                # Check if the number of stickers is correct. Otherwise, wait until next round and remove file
                if received_no_of_stickers + 1 != len(self.other_pack.stickers.documents):
                    os.remove('./message_sticker_files/1.webp')
                    time.sleep(5)
                    continue

                result = content[4:]

                # Check if the newly received data is of a new message
                if received_sequence_number >= self.sequence_number:
                    # Decode the received data
                    for i in range(2, len(self.other_pack.stickers.documents)):
                        self.client.loop.run_until_complete(self.download(
                            self.other_pack.stickers.documents[i], './message_sticker_files/' + str(i)))

                        result += decode_image('./message_sticker_files/' + str(i) + '.webp')

                    # Increment our own sequence number
                    self.sequence_number = received_sequence_number + 1
                    break

                # If the sequence number was incorrect, delete the file
                os.remove('./message_sticker_files/1.webp')

            # Wait 5 seconds
            time.sleep(5)

        shutil.rmtree(path)
        return result

    def close(self):
        """
        Closes the communication channel
        :return: Nothing
        """
        print('[Client "' + self.client_id + '"] Closing channel...')
        self.client.loop.run_until_complete(self.my_pack.delete())
        print('[Client "' + self.client_id + '"] Session closed!')


class StickerPack:
    """
    Represents a Telegram sticker pack

    Attributes:
        client: The Telegram client object
        id: The ID of this sticker pack
        stickers: The list of (unsynchronized) stickers in this sticker pack

    Methods:
        create: Creates this sticker pack on Telegram
        refresh: Synchronizes the stickers in this sticker pack with the 'stickers' attribute
        clear: Clears this sticker pack of all stickers
        add_from_directory: Adds all files in a given directory as stickers for this sticker pack
        delete: Deletes this sticker pack from Telegram
        get_url: Returns the URL of this sticker pack on Telegram
    """

    URL_PREFIX = "https://t.me/addstickers/"
    PREFIX = "RU_TCC_"

    def __init__(self, client: TelegramClient, pack_id: str):
        """
        Initializes this class
        :param client: The Telegram client object
        :param pack_id: The ID of this pack
        """
        self.client = client
        self.id = StickerPack.PREFIX + pack_id
        self.stickers = None

    async def create(self):
        """
        Creates a new sticker pack on telegram using communication with the Stickers bot
        :return: Nothing
        """
        await self.client.send_message('@Stickers', '/newpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_file('@Stickers',
                                    file=os.path.join(os.path.dirname(__file__), 'resources/pack_image.png'),
                                    force_document=True)
        await self.client.send_message('@Stickers', '😀')
        await self.client.send_message('@Stickers', '/publish')
        await self.client.send_message('@Stickers', '/skip')
        await self.client.send_message('@Stickers', self.id)

    async def refresh(self):
        """
        Synchronizes the stickers for this sticker pack on Telegram with the 'stickers' attribute
        :return: Nothing
        """
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
        """
        Clears this sticker pack of all stickers except the first
        :return: Nothing
        """
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
        """
        Adds all files in the given directory as stickers to the sticker pack
        :param path: The path to the directory that the files are stored in
        :return: Nothing
        """
        await self.client.send_message('@Stickers', '/addsticker')
        for sticker in os.listdir(path):
            await self.client.send_message('@Stickers', self.id)
            await self.client.send_file('@Stickers',
                                        file=os.path.join(path, sticker),
                                        force_document=True)
            await self.client.send_message('@Stickers', '😃')
        await self.client.send_message('@Stickers', '/done')

    async def delete(self):
        """
        Deletes this sticker pack from Telegram
        :return: Nothing
        """
        await self.client.send_message('@Stickers', '/delpack')
        await self.client.send_message('@Stickers', self.id)
        await self.client.send_message('@Stickers', 'Yes, I am totally sure.')

    def get_url(self) -> str:
        """
        Retrieves the URL of this sticker pack on Telegram
        :return: The Telegram URL of this sticker pack
        """
        return StickerPack.URL_PREFIX + self.id
