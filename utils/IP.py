# IP file - connections, requests, responses, etc.
import requests
import os
from datetime import datetime as date
from utils.log import *


def attachment_extract(url, name, ext):
    response = requests.get(url)

    if not os.path.exists(ext + '/' + name):
        dir = ext +"/" + name
        os.mkdir(dir)
    path = ext + "/" + name + "/" + ("_".join(str(date.now())[:-7].replace(":", "-").split())) + "." + ext
    with open(path, "wb") as f:
        f.write(response.content)
        return path
