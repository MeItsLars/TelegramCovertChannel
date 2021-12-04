import os
import shutil
from stegano import lsb
from PIL import Image
import numpy as np

from covertchannel.cats import generate_cat


def decode_image(path):
    layer = 1
    image = Image.open(path)

    pixels = np.array([[r, g, b] for (r, g, b) in list(image.getdata())])
    red = pixels[:, 0].reshape((512, 512))
    green = pixels[:, 1].reshape((512, 512))
    blue = pixels[:, 2].reshape((512, 512))
    ru, rs, rvh = np.linalg.svd(red, full_matrices=True)
    gu, gs, gvh = np.linalg.svd(green, full_matrices=True)
    bu, bs, bvh = np.linalg.svd(blue, full_matrices=True)
    print('decoding')
    print((ru[:, layer] * rvh[layer])[:10])
    print(rs[:10])


def encode_in_images(path, data):
    layer = 1
    strength = 1

    generate_cat('./temp.webp')
    image = Image.open('./temp.webp')
    pixels = np.array([[r, g, b] for (r, g, b) in list(image.getdata())])
    red = pixels[:, 0].reshape((512, 512))
    green = pixels[:, 1].reshape((512, 512))
    blue = pixels[:, 2].reshape((512, 512))

    ru, rs, rvh = np.linalg.svd(red, full_matrices=True)
    gu, gs, gvh = np.linalg.svd(green, full_matrices=True)
    bu, bs, bvh = np.linalg.svd(blue, full_matrices=True)

    ru[:, layer] = np.full((512,), 0 * strength)
    rvh[layer] = np.full((512,), 0 * strength)
    gu[:, layer] = np.full((512,), 0 * strength)
    gvh[layer] = np.full((512,), 0 * strength)
    bu[:, layer] = np.full((512,), 0 * strength)
    bvh[layer] = np.full((512,), 0 * strength)

    ru[1, layer] = 1*strength
    rvh[layer, 1] = 1*strength

    print(ru[:10, layer])
    print(rs[:10])

    dred = np.dot(ru * rs, rvh).ravel().astype(int)
    dgreen = np.dot(gu * gs, gvh).ravel().astype(int)
    dblue = np.dot(bu * bs, bvh).ravel().astype(int)

    dpixels = list(zip(dred, dgreen, dblue))
    dimage = Image.new(image.mode, image.size)
    dimage.putdata(dpixels)
    dimage.save(path)





    # # Example code that copies the pack image into 5 separate stickers
    # image_path = os.path.join(os.path.dirname(__file__), 'resources/pack_image.png')
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("1.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("2.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("3.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("4.png")))
    # shutil.copyfile(image_path, os.path.join(path, os.path.basename("5.png")))


encode_in_images('test.webp', 'test')
