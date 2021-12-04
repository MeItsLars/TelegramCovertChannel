from covertchannel.channel import Channel
import json

with open('configuration.json', 'r') as file:
    config = json.load(file)

api_id = config['api_id']
api_hash = config['api_hash']

with open('../client_ids.json', 'r') as file:
    client_ids = json.load(file)

client_id = client_ids['client_1']
other_client_id = client_ids['client_2']

channel = Channel(client_id, api_id, api_hash, other_client_id)
url = channel.initialize()
channel.send_str('Test message')
input("Press enter to continue")
channel.close()
