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

# Loop until the user inputs 'Stop' or the channel is closed by the other client
while True:
    # Retrieve the data that the user wants to send
    data = input('Please enter a message to send (or "Stop" to stop):\n')
    if data == 'Stop':
        break

    # Send the data to the other client
    channel.send(data.encode())

    # Retrieve the result and print it
    result = channel.receive()
    if result is None:
        print('The other party has stopped the communication.')
        break

    print('Received: "' + result.decode() + '"\n')

# Close the channel
channel.close()
