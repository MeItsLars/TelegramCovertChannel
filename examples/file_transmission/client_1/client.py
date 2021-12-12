from covertchannel.channel import Channel
import json

# Load the API configuration
with open('configuration.json', 'r') as file:
    config = json.load(file)

api_id = config['api_id']
api_hash = config['api_hash']

# Load the client IDs
with open('../client_ids.json', 'r') as file:
    client_ids = json.load(file)

client_id = client_ids['client_1']
other_client_id = client_ids['client_2']

# Create and initialize the communication channel
channel = Channel(client_id, api_id, api_hash, other_client_id)
channel.initialize()

# Open and send the file
with open('./file.txt', 'rb') as file:
    data = file.read()
    channel.send(data)

# Close the channel
input("Press enter to continue")
channel.close()
