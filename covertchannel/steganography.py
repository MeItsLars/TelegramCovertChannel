import os
import shutil
from stegano import lsb
from PIL import Image
import numpy as np

from covertchannel.cats import generate_cat


def decode_image(path):
    layer = 1
    block_size = 8

    image = Image.open(path)

    pixels = np.array([[r, g, b] for (r, g, b) in list(image.getdata())], dtype=float)
    red = pixels[:, 0].reshape((512, 512))[:block_size, :block_size]
    green = pixels[:, 1].reshape((512, 512))[:block_size, :block_size]
    blue = pixels[:, 2].reshape((512, 512))[:block_size, :block_size]
    ru, rs, rvh = np.linalg.svd(red, full_matrices=True)
    gu, gs, gvh = np.linalg.svd(green, full_matrices=True)
    bu, bs, bvh = np.linalg.svd(blue, full_matrices=True)
    print('decoding')
    print(ru)
    print(rs)


def make_orthogonal(v1, v2, size):
    dot_product = np.dot(v1, v2)
    print(dot_product)
    a = v1[size-1]
    b = v2[size-1]
    v2[size-1] = ((a*b)-dot_product)/a
    print(np.dot(v1, v2))
    return v2

def encode_in_images(path, data):
    layer = 1
    strength = 1
    block_size = 8

    generate_cat('./temp.webp')
    image = Image.open('./temp.webp')
    pixels = np.array([[r, g, b] for (r, g, b) in list(image.getdata())], dtype=float)
    red = pixels[:, 0].reshape((512, 512))[:block_size, :block_size]
    green = pixels[:, 1].reshape((512, 512))[:block_size, :block_size]
    blue = pixels[:, 2].reshape((512, 512))[:block_size, :block_size]

    ru, rs, rvh = np.linalg.svd(red, full_matrices=True)
    gu, gs, gvh = np.linalg.svd(green, full_matrices=True)
    bu, bs, bvh = np.linalg.svd(blue, full_matrices=True)

    #ru[1, layer] = 1*strength
    #ru[:, layer] = make_orthogonal(ru[:, 0], ru[:, layer], block_size)
    #ru[:, layer+1:] = np.full(shape=(block_size, block_size - layer - 1), fill_value=0.)
    rs[2:] = np.full((6,), 0)

    print('encoding')
    print(ru)
    print(rs)

    dred = pixels[:, 0].reshape((512, 512))
    dred[:block_size, :block_size] = np.dot(ru * rs, rvh)
    dgreen = pixels[:, 1].reshape((512, 512))
    dgreen[:block_size, :block_size] = np.dot(gu * gs, gvh)
    dblue = pixels[:, 2].reshape((512, 512))
    dblue[:block_size, :block_size] = np.dot(bu * bs, bvh)

    dpixels = list(zip(np.around(dred.ravel()).astype(int), np.around(dgreen.ravel()).astype(int),
                       np.around(dblue.ravel()).astype(int)))
    testpixels = list(zip(dred.ravel(), dgreen.ravel(), dblue.ravel()))


    dimage = Image.new(image.mode, image.size)
    dimage.putdata(dpixels)
    dimage.save(path)
    os.remove('./temp.webp')





    # # Example code that copies the pack image into 5 separate stickers
    # image_path = os.path.join(os.path.dirname(__file__), 'resources/pack_image.png')
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("1.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("2.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("3.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("4.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("5.png")))


encode_in_images('test.webp', 'test')
decode_image('test.webp')
