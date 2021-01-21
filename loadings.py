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
    return data


def load_map(map_id):
    con = sqlite3.connect(os.path.join('Maps', 'maps.db'))
    cur = con.cursor()
    map_name = cur.execute(f'''select way from maps where id={map_id}''').fetchone()[0]
    txt_way = os.path.join('Maps', map_name)
    with open(txt_way, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        data = [list(map(int, i[0].split())) for i in list(reader)]
    return data


def upload_results(map_id, weapons):
    con = sqlite3.connect('weapons.db')
    cur = con.cursor()
    ids = []
    for weap in weapons:
        id = cur.execute(f'''select id from weapons where title={weap.title}''').fetchone()[0]
        ids.append(id)
    with open('res.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"')
        writer.writerow(map_id + '\n' + ' '.join(ids))


def load_weapon(weapon_id):
    con = sqlite3.connect('weapons.db')
    cur = con.cursor()
    weap = list(cur.execute(f'''select title, damage, radius, image, velocity from weapons
                                            where id={weapon_id}''').fetchone())
    weap[3] = load_image(weap[3])
    return weap
