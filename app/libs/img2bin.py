import os

import psycopg2

from settings import photo_path


def img2bin(photo, rule):
    with open(os.path.join(photo_path + rule, photo), 'rb') as f:
        img = f.read()
    return psycopg2.Binary(img)
