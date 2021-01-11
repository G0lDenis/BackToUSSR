import pygame
import sys
import os
import loadings


def terminate():
    pygame.quit()
    sys.exit()


class MainMenu:
    pass


class Room:
    def __init__(self, name):
        self.map = loadings.load_map(name)
        self.width = self.map.width
        self.height = self.map.height
        self.tile_width = self.map.tilewidth
        self.tile_height = self.map.tileheight

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                im = self.map.get_tile_image(x, y, 0)


class Enemy:
    pass


class MainHero:
    def __init__(self):
        pass


if __name__ == '__main__':
    pygame.init()
    FPS = 50
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
