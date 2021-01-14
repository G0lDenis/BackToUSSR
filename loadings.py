import csv
import pygame
import os


def load_image(name):
    fullname = os.path.join('Images', name)
    im = pygame.image.load(fullname)
    return im


def load_results():
    global data
    with open('res.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        data = list(reader)


def load_map(map_name):
    txt_way = os.path.join('Maps', map_name)
    with open(txt_way, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        data = [list(map(int, i[0].split())) for i in list(reader)]
    return data
