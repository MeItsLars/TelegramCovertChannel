from telethon import TelegramClient, events, sync

api_id = 8205533
api_hash = 'e0750e29f8b159ac273dc072e0541e67'

client = TelegramClient('current', api_id, api_hash)
client.start()

client.send_message('@Stickers', '/newpack')
client.send_message('@Stickers', 'SuperSecretCovertChannel')
client.send_file('@Stickers', './pack_image.png', force_document=True)
client.send_message('@Stickers', '😉')
client.send_message('@Stickers', '/publish')
client.send_message('@Stickers', '/skip')
client.send_message('@Stickers', 'SuperSecretCovertChannel')

print('Done!')

