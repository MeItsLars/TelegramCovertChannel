import os

import requests
import urllib.request

from PIL import Image
from resizeimage import resizeimage

url = "https://api.thecatapi.com/v1/images/search"
params = {
    "size": "full",
    "mime_types": "png"
}


def generate_cat(path, filename: str):
    path = os.path.join(path, filename)

    resp = requests.get(url, params)
    data = resp.json()

    while data[0]['width'] < 512 or data[0]['height'] < 512:
        resp = requests.get(url, params)
        data = resp.json()

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(data[0]['url'], path)

    with open(path, 'r+b') as file:
        with Image.open(file) as image:
            cover = resizeimage.resize_cover(image, [512, 512])
            cover.save(path, image.format)
