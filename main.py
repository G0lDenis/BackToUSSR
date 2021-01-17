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
    def __init__(self, name, damage, radius, img_path):
        self.name = name
        self.damage = damage
        self.radius = radius
        self.img_path = img_path

    def draw(self):
        im = pygame.image.load(self.img_path)
        self.spr = pygame.sprite.Sprite()
        self.spr.image = im
        self.spr.rect = self.spr.image.get_rect()
        self.spr.rect.x, self.spr.rect.y = (10, screen.get_height() - 100)
        invent.add(self.spr)
        im = pygame.transform.scale(im, (im.get_width() // 5, im.get_height() // 5))
        self.sm_spr = pygame.sprite.Sprite()
        self.sm_spr.image = im
        self.sm_spr.rect = self.spr.image.get_rect()

    def drop(self):
        all_sprites.add(self.sm_spr)
        self.sm_spr.rect.x, self.sm_spr.rect.y = hero.rect.x, hero.rect.y
        droped_weapon.append([hero.weapons[hero.slot_number], hero.rect.x, hero.rect.y])
        invent.remove(hero.weapons[hero.slot_number].spr)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, dest_x, dest_y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((7, 5))
        self.image.fill('#c9b500')
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.dest_x = dest_x
        self.dest_y = dest_y
        if dest_x > hero.rect.x:
            self.speed_x = 10
        else:
            self.speed_x = -10
        self.speed_y = 0
        self.weapon = weapon
        self.find_path()

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        square_go_x = math.fabs(self.rect.x - self.x) ** 2
        square_go_y = math.fabs(self.rect.y - self.y) ** 2
        go = math.sqrt(square_go_x + square_go_y)
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.top > screen.get_height() or self.rect.left > screen.get_width() or go > self.weapon.radius:
            self.kill()

    def find_path(self):
        len_x = self.dest_x - self.x
        len_y = self.dest_y - self.y
        if len_x == 0:
            self.speed_x = 0
        elif len_y == 0:
            self.speed_y = 0
        else:
            points_up = len_x // self.speed_x
            if points_up != 0:
                self.speed_y = len_y / points_up
            else:
                points_up += 1
                self.speed_y = len_y / points_up


class MainHero(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.weapons = [Weapon('simple pistol', 10, 200, 'Images/default_pistol.png'),
                        Weapon('AK-47', 10, 200, 'Images/ak-47.png'), Weapon('AK-47', 10, 200, 'Images/ak-47.png')]
        self.slot_number = 1
        self.pos = pos
        self.side = 'right'
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
        self.image = self.frames[self.cur_frame]
        self.rotate_image(pygame.mouse.get_pos())
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        if pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 9
            self.side = 'left'
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 9
            self.side = 'right'
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 9
            self.side = 'up'
            self.moving = True
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 9
            self.side = 'down'
            self.moving = True
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        else:
            self.cur_frame = 0
        self.rect = self.rect.move(next_x, next_y)
        if pygame.sprite.spritecollideany(self, obstacles) is not None or not self.in_field():
            self.rect = self.rect.move(-next_x, -next_y)
        self.moving = False

    def in_field(self):
        if self.rect.x < 0 or self.rect.x + self.rect.w > 1024 or \
                self.rect.y < 0 or self.rect.y + self.rect.h > 768:
            return False
        return True

    def rotate_image(self, pos):
        rel_x, rel_y = pos[0] - self.rect.x, pos[1] - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.image, int(angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, go_to):
        bullet = Bullet(self.rect.centerx, self.rect.centery, hero.weapons[hero.slot_number], go_to[0], go_to[1])
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
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()

    obstacles = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
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
                                    hero.weapons[hero.slot_number].drop()
                                    a = hero.weapons[hero.slot_number]
                                    hero.weapons[hero.slot_number] = droped_weapon[i][0]
                                    all_sprites.add(droped_weapon[i][0].sm_spr)
                                    del droped_weapon[i]

        camera.update(hero)
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
