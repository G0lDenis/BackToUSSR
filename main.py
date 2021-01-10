import pygame
import sys
import os


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name):
    fullname = os.path.join('Images', name)
    im = pygame.image.load(fullname)
    return im


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
