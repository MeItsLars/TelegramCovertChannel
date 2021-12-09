import os

import numpy as np
from PIL import Image

from covertchannel.cats import generate_cat


def decode_image(path) -> bytes:
    image = Image.open(path)
    bits = ''.join([str((255-a)) for (r, g, b, a) in list(image.getdata())]).split('2')[0]
    data = bytes(int(bits[i: i + 8], 2) for i in range(0, len(bits), 8))

    return data


def encode_sticker(path, data: bytes):
    generate_cat('./temp.webp')
    with Image.open('./temp.webp') as image:
        a_channel = Image.new('L', image.size, 255)
        a_pixels = list(a_channel.getdata())

        bitstring = ''.join(format(byte, '08b') for byte in data)
        bits = [int(c) for c in bitstring]
        bits.append(2)
        a_pixels = np.array(a_pixels) + (np.pad(bits, (0, (512*512)-len(bits)), 'constant', constant_values=(0, )) * -1)

        a_channel.putdata(a_pixels)

        image.putalpha(a_channel)
        image.save(path, **image.info)

    os.remove('./temp.webp')

