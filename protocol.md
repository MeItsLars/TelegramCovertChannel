# Telegram Covert Channel Messaging Protocol
## General
This protocol can be applied when two parties want to communicate in secret, and they both have access to Telegram.
It makes use of Telegram Sticker Packs and hides the messaging packets in these stickers.
It assumes the two parties have unique IDs and that the two communicating parties know each others IDs.
In this document, we'll call these IDs 'IdA' and 'IdB', for the first and second party respectively.

## Initialization
As a sticker pack can only be edited by its creator, the initialization of the channel consists of 
each of the parties creating a sticker pack, which we will call 'PackA' and 'PackB'.
In Telegram, sticker packs can be found by their ID.
In a communication session between party A and B, the sticker pack ID of the pack that A creates is 'RU_TCC_IdA_IdB'.
The sticker pack ID of the pack that B creates is 'RU_TCC_IdB_IdA'.
This way, only the two communicating parties know of the existence of the sticker packs.

After the sticker packs have been created, both parties subscribe to both sticker packs, so they can read their contents.
PackA is used for messages from A to B, and PackB is used for messages from B to A.

## Communication
### Steganography
The sticker packs allow for raw data to be hidden inside the stickers.
This data is stored using a general technique called steganography.
More specific, the alpha value (which determines transparency) of each pixel can be used to hide data in.
In our implementation, the alpha value is either 255 or 254. The difference is undetectable to the human eye.
The data we are sending is converted to binary, and encoded in these alpha values, where a zero bit becomes 254,
and a one bit becomes 255.

### Message
Messages are packets, that use the following packet header:
```
+-------------------------------------------------+-------------------------------------------------+
| 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 | 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 |
+-------------------------------------------------+-------------------------------------------------+
|                Sequence Number                  |                  Content Length                 |
+-------------------------------------------------+-------------------------------------------------+
\                                          Message Data                                             \
+-------------------------------------------------+-------------------------------------------------+
```
The sequence number is a 2-byte unsigned short which represents the ID of the current message. 
Each time a new message is transmitted, it is incremented by one.
The content length is a 2-byte unsigned short which represents the length of the data (in bytes) in the message.
The message data ia a byte array which represents the rest of the data.
It can not be longer than 3.932.156 bytes.
The reasoning behind this number can be found in the 'Statistics' section for this protocol.
After constructing the packet, the packet is encoded into the stickers as described in the 'Steganography' section.

The first message is always sent by the party that has the lowest ID. The ID of this message should be 0.
Only upon receiving a message is a party allowed to increment the sequence number and send a new message.
The sequence number should be the sequence number of the message received last, plus one.
This way, no party can ever override a message they have sent without the other party having read that message.
If a party, after receiving a message, wants to wait for more data, they can send an empty packet as a response,
to indicate to the other party that they have received the original message.

## Finalization
When the conversation is finished, the two sticker packs PackA and PackB are deleted.
This destroys the communicated data, and all traces of the communication.

## Statistics
### Maximum message size
As the stickers are 512 pixels high and 512 pixels wide, we have 262.144 pixels (thus bits) to work with.
This gives us 32.768 bytes per sticker.
As there can be 120 stickers in a sticker pack, this gives us a maximum message size of 3.932.160 bytes,
or roughly 4 MB. It is also possible to send more data, but that would require multiple messages.