# IP file - connections, requests, responses, etc.
import requests
import os
from datetime import datetime as date


def attachment_extract(url, name):
    response = requests.get(url)
    if not os.path.exists('xlsx/' + name):
        dir = 'xlsx/' + name
        os.mkdir(dir)
        print("новый клуб: " + name)
    path = "xlsx/" + name + "/" + ("_".join(str(date.now())[:-7].replace(":", "-").split())) + ".xlsx"
    with open(path, "wb") as f:
        f.write(response.content)
        return path
