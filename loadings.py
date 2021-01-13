import csv
import pygame
import pytmx
import os


def load_map_name(name):
    return os.path.join('Maps', name)


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
    map = pytmx.load_pygame(load_map_name(map_name))
    return map
