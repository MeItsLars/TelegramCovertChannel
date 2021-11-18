import os
import shutil


def encode_in_images(path, data: bytes):
    # Example code that copies the pack image into 5 separate stickers
    image_path = os.path.join(os.path.dirname(__file__), 'resources/pack_image.png')
    shutil.copyfile(image_path, os.path.join(path, os.path.basename("1.png")))
    shutil.copyfile(image_path, os.path.join(path, os.path.basename("2.png")))
    shutil.copyfile(image_path, os.path.join(path, os.path.basename("3.png")))
    shutil.copyfile(image_path, os.path.join(path, os.path.basename("4.png")))
    shutil.copyfile(image_path, os.path.join(path, os.path.basename("5.png")))
