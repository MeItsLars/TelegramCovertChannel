import os
import shutil
from stegano import lsb
from PIL import Image
import numpy as np

from covertchannel.cats import generate_cat


def decode_image(path):
    image = Image.open(path)
    bits = ''.join([str((255-a)) for (r, g, b, a) in list(image.getdata())]).split('2')[0]
    print(bits[:100])
    data = bytes(int(bits[i: i + 8], 2) for i in range(0, len(bits), 8))

    return data


def make_orthogonal(v1, v2, size):
    dot_product = np.dot(v1, v2)
    print(dot_product)
    a = v1[size-1]
    b = v2[size-1]
    v2[size-1] = ((a*b)-dot_product)/a
    print(np.dot(v1, v2))
    return v2


def encode_in_images(path, data: bytes):
    generate_cat('./temp.webp')
    image = Image.open('./temp.webp')

    a_channel = Image.new('L', image.size, 255)
    a_pixels = list(a_channel.getdata())

    bitstring = ''.join(format(byte, '08b') for byte in data)
    print(bitstring[:100])
    bits = [int(c) for c in bitstring]
    bits.append(2)
    a_pixels = np.array(a_pixels) + (np.pad(bits, (0, (512*512)-len(bits)), 'constant', constant_values=(0, )) * -1)

    a_channel.putdata(a_pixels)

    image.putalpha(a_channel)
    image.save(path, **image.info)
    os.remove('./temp.webp')





    # # Example code that copies the pack image into 5 separate stickers
    # image_path = os.path.join(os.path.dirname(__file__), 'resources/pack_image.png')
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("1.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("2.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("3.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("4.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("5.png")))

