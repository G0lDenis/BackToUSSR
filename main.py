import pygame
import sys
import math

size = width, height = 1200, 675
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Back To USSR')
all_sprites = pygame.sprite.Group()
SPEED = 6
screen.fill((255, 255, 255))
last_angle = 0
keys = {
    pygame.K_w: False,
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False,
}


def rotate(img, pos, angle):
    w, h = img.get_size()
    img2 = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
    img2.blit(img, (w - pos[0], h - pos[1]))
    return pygame.transform.rotate(img2, angle)


class hero:
    def __init__(self, weapon, x, y, img_path, hp):
        self.weapon = weapon
        self.x = x
        self.y = y
        self.im = pygame.image.load(img_path)
        self.hp = hp
        self.spr = pygame.sprite.Sprite()
        self.spr.image = self.im
        self.spr.rect = self.spr.image.get_rect()
        all_sprites.add(self.spr)
        self.pos = 'up'

    def update(self):
        self.spr.rect.x = self.x
        self.spr.rect.y = self.y


class weapon:
    def __init__(self, name, damage, radius):
        self.name = name
        self.damage = damage
        self.radius = radius


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main_hero = hero(weapon('fists', 20, 5), 10, 10, 'images/good_stay.png', 180)
    main_hero.spr.image = pygame.transform.rotozoom(main_hero.im, 180, 1)
    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - main_hero.x, mouse_y - main_hero.y
        angle = math.atan2(rel_y, rel_x)
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        main_hero.spr.image = pygame.transform.rotozoom(main_hero.im, angle, 1)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            if ev.type == pygame.KEYDOWN:
                keys[ev.key] = True
            if ev.type == pygame.KEYUP:
                keys[ev.key] = False
            if keys[pygame.K_w] and main_hero.y > 0:
                main_hero.y -= SPEED
            if keys[pygame.K_s] and main_hero.y < height - 88:
                main_hero.y += SPEED
            if keys[pygame.K_a] and main_hero.x > 0:
                main_hero.x -= SPEED
            if keys[pygame.K_d] and main_hero.x < width - 96:
                main_hero.x += SPEED
        main_hero.update()
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        pygame.display.flip()
