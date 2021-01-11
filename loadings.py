import csv
import pygame
import pytmx
import os


def load_file(name):
    return os.path.join(name, 'Images')


def load_image(name):
    fullname = load_file(name)
    im = pygame.image.load(fullname)
    return im


def load_results():
    global data
    with open('res.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        data = list(reader)


def load_map(map_name):
    map = pytmx.load_pygame(load_file(map_name))
    return map
