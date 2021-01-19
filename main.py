import pygame
import sys
import loadings
import sqlite3
import os
import math
import random

def terminate():
    pygame.quit()
    sys.exit()


def collide_with_mask(spr1, spr2):
    if pygame.sprite.collide_mask(spr1, spr2):
        return True
    return False


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
        for dat in data:
            self.sl[dat[0]] = [dat[1], dat[2]]


class Enemy:
    pass


class Weapon:
    def __init__(self, name, damage, radius, img, velocity):
        self.name = name
        self.damage = damage
        self.radius = radius
        self.velocity = velocity
        self.img = img
        self.spr = pygame.sprite.Sprite()
        self.spr.image = self.img
        self.spr.rect = self.spr.image.get_rect()
        self.spr.rect.x, self.spr.rect.y = (10, screen.get_height() - 100)
        im = pygame.transform.scale(self.img, (self.img.get_width() // 3, self.img.get_height() // 3))
        self.sm_spr = pygame.sprite.Sprite()
        self.sm_spr.image = im
        self.sm_spr.rect = self.spr.image.get_rect()

    def drop(self, x, y):
        all_sprites.add(self.sm_spr)
        self.sm_spr.rect.x, self.sm_spr.rect.y = x, y
        droped_weapon.append([hero.weapons[hero.slot_number], hero.rect.x, hero.rect.y])
        invent.remove(hero.weapons[hero.slot_number].spr)

    def draw(self):
        invent.add(self.spr)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, cos, sin, rng):
        super().__init__()
        if rng != 0:
            self.cos = cos + rng
            self.sin = sin + rng
        else:
            self.cos = cos
            self.sin = sin
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, '#c9b500', (5, 5), 5)
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.weapon = weapon
        self.distance = 0

    def update(self):
        self.rect.y += int(self.weapon.velocity * self.sin)
        self.rect.x += int(self.weapon.velocity * self.cos)
        self.distance += self.weapon.velocity
        if pygame.sprite.spritecollideany(self, obstacles,
                                          collided=collide_with_mask) or self.distance > self.weapon.radius:
            self.kill()


class MainHero(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.weapons = [Weapon('simple pistol', 10, 400, loadings.load_image('default_pistol.png'), 10),
                        Weapon('AK-47', 30, 600, loadings.load_image('ak-47.png'), 20), Weapon('Machine-gun', 10, 400, loadings.load_image('machine-gun.png'), 13)]
        self.slot_number = 0
        self.pos = pos
        self.side = 'right'
        self.cur_frame = 0
        self.frames = []
        self.cut_sheet(loadings.load_image('main_hero_sp.png'))
        self.moving = False
        all_sprites.add(self)
        self.mask = None
        self.hp = 100

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
            next_x -= 5
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 5
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 5
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 5
            self.moving = True
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        else:
            self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rotate_image(pygame.mouse.get_pos())
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.rect.move(next_x, next_y)
        if pygame.sprite.spritecollideany(self, obstacles, collided=collide_with_mask) is not None:
            self.rect = self.rect.move(-next_x, -next_y)
        self.moving = False

    def rotate_image(self, pos):
        rel_x, rel_y = pos[0] - self.rect.x, pos[1] - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, go_to):
        delta_x = go_to[0] - self.rect.x
        delta_y = go_to[1] - self.rect.y
        rad = math.sqrt(delta_x ** 2 + delta_y ** 2)
        rng = 0
        if hero.weapons[hero.slot_number].name == 'Machine-gun':
            rng = random.uniform(-0.2, 0.2)
            print(rng)
        if delta_x and delta_y:
            bullet = Bullet(self.rect.centerx, self.rect.centery, hero.weapons[hero.slot_number], (delta_x / rad),
                            (delta_y / rad), rng)
            all_sprites.add(bullet)
            hero_bullets.add(bullet)


class Game:
    def __init__(self, in_room, in_hero):
        self.room = in_room
        self.hero = in_hero

    def render(self):
        self.hero.update_hero()
        for bull in hero_bullets:
            bull.update()
        self.room.render()
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        draw_hp(screen)
        invent.draw(screen)


def draw_hp(in_screen):
    # pygame.draw.rect(in_screen, pygame.Color(10, 0, 250, a=100), (0, 668, 1024, 100))
    pygame.draw.rect(in_screen, (204, 0, 0), (300, 688, hero.hp * 2, 40))
    pygame.draw.rect(in_screen, (204, 0, 0), (300, 688, 200, 40), 3)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        if target.rect.x < 64:
            target.rect.x = 65
        if target.rect.y < 64:
            target.rect.y = 65
        l_u_cell = obstacles.sprites()[0]
        r_d_cell = obstacles.sprites()[115]
        if (l_u_cell.rect.x >= 0 and target.rect.x < width // 2) or \
                (r_d_cell.rect.x <= width - r_d_cell.rect.w):
            self.dx = 0
        else:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)

        if (l_u_cell.rect.y >= 0 and target.rect.y < height // 2) or \
                (r_d_cell.rect.y <= height - r_d_cell.rect.h):
            self.dy = 0
        else:
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


if __name__ == '__main__':
    pygame.init()
    FPS = 20
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()
    cells = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    hero_bullets = pygame.sprite.Group()
    invent = pygame.sprite.Group()
    droped_weapon = []
    room = Room('f-r.txt')
    hero = MainHero((0, 3 * room.tile_height))
    game = Game(room, hero)
    pygame.display.flip()
    hero.weapons[hero.slot_number].draw()
    clock = pygame.time.Clock()
    camera = Camera()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                hero.shoot(pygame.mouse.get_pos())

            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_q:
                    invent.remove(hero.weapons[hero.slot_number].spr)
                    if hero.slot_number < len(hero.weapons) - 1:
                        hero.slot_number += 1
                    else:
                        hero.slot_number = 0
                    hero.weapons[hero.slot_number].draw()
                    print(hero.slot_number)
                if ev.key == pygame.K_g:
                    if hero.weapons[hero.slot_number].name != 'simple pistol':
                        hero.weapons[hero.slot_number].drop()
                        del hero.weapons[hero.slot_number]
                        hero.slot_number -= 1
                        hero.weapons[hero.slot_number].draw()
                elif ev.key == pygame.K_f:
                    for i in range(len(droped_weapon)):
                        square_go_x = math.fabs(droped_weapon[i][0].sm_spr.rect.x - hero.rect.x) ** 2
                        square_go_y = math.fabs(droped_weapon[i][0].sm_spr.rect.y - hero.rect.y) ** 2
                        go = math.sqrt(square_go_x + square_go_y)
                        if go <= 20:
                            all_sprites.remove(droped_weapon[i][0].sm_spr)
                            if len(hero.weapons) < 3:
                                invent.remove(hero.weapons[hero.slot_number].spr)
                                hero.weapons.append(droped_weapon[i][0])
                                droped_weapon[i][0].draw()
                                del droped_weapon[i]
                                hero.slot_number = len(hero.weapons) - 1
                            else:
                                if hero.weapons[hero.slot_number].name != 'simple pistol':
                                    droped_weapon[i][0].draw()
                                    hero.weapons[hero.slot_number].drop(hero.rect.x, hero.rect.y)
                                    a = hero.weapons[hero.slot_number]
                                    hero.weapons[hero.slot_number] = droped_weapon[i][0]
                                    all_sprites.add(droped_weapon[i][0].sm_spr)
                                    del droped_weapon[i]

        camera.update(hero)
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
