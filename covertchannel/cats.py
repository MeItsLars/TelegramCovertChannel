import urllib.request

import requests
from PIL import Image
from resizeimage import resizeimage

url = "https://api.thecatapi.com/v1/images/search"
params = {
    "size": "full",
    "mime_types": "jpeg"
}


def generate_cat(path):
    """
    Generates a new cat image using the 'thecatapi' API and save it to a file
    :param path: The path of the file that the resulting cat image should be stored in
    :return: Nothing
    """

    # Create a request and retrieve the data
    resp = requests.get(url, params)
    data = resp.json()

    # Check that the width and height are at least 512. If not, create a new request and repeat until the size is right
    while data[0]['width'] < 512 or data[0]['height'] < 512:
        resp = requests.get(url, params)
        data = resp.json()

    # Take the image URL from the response, and download the image to the path file
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(data[0]['url'], path)

    # Resize the image to exactly 512x512 pixels
    with open(path, 'r+b') as file:
        with Image.open(file) as image:
            cover = resizeimage.resize_cover(image, [512, 512])
            cover.save(path, image.format)
