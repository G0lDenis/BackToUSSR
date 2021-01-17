import pygame
import sys
import loadings
import sqlite3
import os
import math


def terminate():
    pygame.quit()
    sys.exit()


class Cell(pygame.sprite.Sprite):
    def __init__(self, im, x, y, w, h):
        super().__init__()
        self.image = im
        self.rect = pygame.Rect(x, y, w, h)


class Room:
    def __init__(self, name):
        self.map = loadings.load_map(name)
        self.sl = {}
        self.load_sql()
        self.width = 32
        self.height = 24
        self.tile_width = 64
        self.tile_height = 64
        self.show()

    def show(self):
        for y in range(self.height):
            for x in range(self.width):
                im = loadings.load_image(self.sl[self.map[y][x]][0])
                cell = Cell(im, x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
                all_sprites.add(cell)
                if not self.sl[self.map[y][x]][1]:
                    obstacles.add(cell)
                else:
                    cells.add(cell)

    def render(self):
        pass

    def load_sql(self):
        con = sqlite3.connect(os.path.join('Maps', 'maps.db'))
        cur = con.cursor()
        data = cur.execute('''select * from maps''')
        for i in data:
            self.sl[i[0]] = [i[1], i[2]]


class Enemy:
    pass


class Weapon:
    def __init__(self, name, damage, radius, img, velocity):
        self.name = name
        self.damage = damage
        self.radius = radius
        self.velocity = velocity
        self.spr = pygame.sprite.Sprite()
        self.spr.image = img
        self.spr.rect = self.spr.image.get_rect()
        invent.add(self.spr)
        self.spr.rect.x, self.spr.rect.y = (10, screen.get_height() - 100)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, cos, sin):
        super().__init__()
        self.cos = cos
        self.sin = sin
        self.image = pygame.Surface((7, 5))
        self.image.fill('#c9b500')
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.weapon = weapon
        self.distance = 0

    def update(self):
        self.rect.y += int(self.weapon.velocity * self.sin)
        self.rect.x += int(self.weapon.velocity * self.cos)
        self.distance += self.weapon.velocity
        if pygame.sprite.spritecollideany(self, obstacles) or self.distance > self.weapon.radius:
            self.kill()


class MainHero(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.weapons = [Weapon('simple pistol', 10, 200, loadings.load_image('default_pistol.png'), 15)]
        self.slot_number = 0
        self.pos = pos
        self.cur_frame = 0
        self.frames = []
        self.cut_sheet(loadings.load_image('main_hero_sp.png'))
        self.moving = False
        all_sprites.add(self)
        self.mask = None

    def cut_sheet(self, sheet):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 3,
                                sheet.get_height())
        for j in range(3):
            frame_location = (self.rect.w * j, 0)
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))

    def update_hero(self):
        next_x, next_y = 0, 0
        if pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 9
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 9
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 9
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 9
            self.moving = True
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        else:
            self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rotate_image(pygame.mouse.get_pos())
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.rect.move(next_x, next_y)
        if pygame.sprite.spritecollideany(self, obstacles) is not None:
            self.rect = self.rect.move(-next_x, -next_y)
        self.moving = False

    def rotate_image(self, pos):
        rel_x, rel_y = pos[0] - self.rect.x, pos[1] - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.image, int(angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, go_to):
        delta_x = go_to[0] - self.rect.x
        delta_y = go_to[1] - self.rect.y
        rad = math.sqrt(delta_x ** 2 + delta_y ** 2)
        if delta_x and delta_y:
            bullet = Bullet(self.rect.centerx, self.rect.centery, hero.weapons[hero.slot_number], delta_x / rad,
                            delta_y / rad)
            all_sprites.add(bullet)
            bullets.add(bullet)


class Game:
    def __init__(self, in_room, in_hero):
        self.room = in_room
        self.hero = in_hero

    def render(self):
        self.hero.update_hero()
        for i in bullets:
            i.update()
        self.room.render()
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        invent.draw(screen)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        if target.rect.x < 64:
            target.rect.x = 64
        if target.rect.y < 64:
            target.rect.y = 64
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()
    cells = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    invent = pygame.sprite.Group()
    room = Room('f-r.txt')
    hero = MainHero((0, 3 * room.tile_height))
    game = Game(room, hero)
    pygame.display.flip()
    clock = pygame.time.Clock()
    camera = Camera()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                hero.shoot(pygame.mouse.get_pos())
        camera.update(hero)
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
