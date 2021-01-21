import csv
import pygame
import os
import sqlite3


def load_image(name):
    fullname = os.path.join('Images', name)
    im = pygame.image.load(fullname)
    return im


def load_results():
    with open('res.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        data = list(reader)
    print(data)
    return data


def load_map(map_id):
    print(os.path.join('Maps', 'maps.db'))
    con = sqlite3.connect(os.path.join('Maps', 'maps.db'))
    cur = con.cursor()
    map_name = cur.execute(f'''select way from maps where id={map_id}''').fetchone()[0]
    txt_way = os.path.join('Maps', map_name)
    with open(txt_way, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        data = [list(map(int, i[0].split())) for i in list(reader)]
    return data
