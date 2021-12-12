import os

import numpy as np
from PIL import Image

from covertchannel.cats import generate_cat


def decode_image(path) -> bytes:
    """
    Decodes the given image into bytes, using alpha-channel steganography
    :param path: The path to the image file
    :return: The data that was encoded in the image, as a byte array
    """
    # Open the image
    image = Image.open(path)
    # Retrieve all encoded bits
    bits = ''.join([str((255-a)) for (r, g, b, a) in list(image.getdata())]).split('2')[0]
    # Convert the bits to bytes
    data = bytes(int(bits[i: i + 8], 2) for i in range(0, len(bits), 8))
    return data


def encode_sticker(path, data: bytes):
    """
    Encodes the given data into a given file using alpha-channel steganography
    :param path: The path to the file that the result will be in
    :param data: The data we want to encode into the file
    :return: Nothing
    """
    # Generate a random cat image to encode the data in
    generate_cat('./temp.webp')
    with Image.open('./temp.webp') as image:
        # Open the alpha channel and list its pixels
        a_channel = Image.new('L', image.size, 255)
        a_pixels = list(a_channel.getdata())

        # Convert the input data into a bit string
        bitstring = ''.join(format(byte, '08b') for byte in data)
        bits = [int(c) for c in bitstring]

        # If the length of the bit string is smaller than the maximum number of pixels, add a '2' to indicate the end
        if len(bits) < 512 * 512:
            bits.append(2)
        # Append the bit string to the alpha channel
        a_pixels = np.array(a_pixels) + (np.pad(bits, (0, (512*512)-len(bits)), 'constant', constant_values=(0, )) * -1)

        # Store the alpha channel and save the image
        a_channel.putdata(a_pixels)
        image.putalpha(a_channel)
        image.save(path, **image.info)

    # Remove the temporary cat image file
    os.remove('./temp.webp')

