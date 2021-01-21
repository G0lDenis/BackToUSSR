import pygame
import sys
import loadings
import sqlite3
import os
import math
from random import randrange, uniform
from end import lose
from titles_beg import start_titles


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
        self.image = im.convert()
        self.rect = pygame.Rect(x, y, w, h)


class Room:
    def __init__(self, id):
        self.map = loadings.load_map(id)
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
                all_cells.add(cell)
                if not self.sl[self.map[y][x]][1]:
                    obstacles.add(cell)
                else:
                    cells.add(cell)

    def render(self):
        pass

    def load_sql(self):
        con = sqlite3.connect(os.path.join('Maps', 'maps.db'))
        cur = con.cursor()
        data = cur.execute('''select * from map_tiles''')
        for dat in data:
            self.sl[dat[0]] = [dat[1], dat[2]]


class Weapon:
    def __init__(self, name, damage, radius, img, velocity):
        self.name = name
        self.damage = damage
        self.radius = radius
        self.velocity = velocity
        self.img = img
        self.spr = pygame.sprite.Sprite()
        self.spr.image = self.img.convert_alpha()
        self.spr.rect = self.spr.image.get_rect()
        self.spr.rect.x, self.spr.rect.y = (10, screen.get_height() - 100)
        im = pygame.transform.scale(self.img, (self.img.get_width() // 3, self.img.get_height() // 3))
        self.sm_spr = pygame.sprite.Sprite()
        self.sm_spr.image = im.convert_alpha()
        self.sm_spr.rect = self.spr.image.get_rect()

    def drop(self, x, y):
        im = pygame.transform.scale(self.img, (self.img.get_width() // 3, self.img.get_height() // 3))
        self.sm_spr = pygame.sprite.Sprite()
        self.sm_spr.image = im.convert_alpha()
        self.sm_spr.rect = self.spr.image.get_rect()
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
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.centery = y
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


class InvisBullet(pygame.sprite.Sprite):
    def __init__(self, pos, rad):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], 1, 1)
        self.image = pygame.Surface((1, 1))
        self.rad = rad

    def check_avail(self, pos):
        dist = 0
        while not (pygame.sprite.spritecollideany(self, obstacles,
                                                  collided=collide_with_mask) or
                   pygame.sprite.collide_mask(self, hero)) and dist <= self.rad:
            delta_x = self.rect.centerx - pos[0]
            delta_y = self.rect.centery - pos[1]
            if delta_x:
                delta_x = (delta_x // abs(delta_x)) * 5
            if delta_y:
                delta_y = (delta_y // abs(delta_y)) * 5
            dist += math.sqrt(delta_x ** 2 + delta_y ** 2)
            self.rect = self.rect.move(-delta_x, -delta_y)
        if self.rect.colliderect(hero.rect):
            return True
        return False


class Character(pygame.sprite.Sprite):
    def __init__(self, type_ch):
        super().__init__()
        all_sprites.add(self)
        if type_ch == 'enemy':
            enemies.add(self)
            con = sqlite3.connect('weapons.db')
            cur = con.cursor()
            self.weapon = list(cur.execute(f'''select title, damage, radius, image, velocity from weapons
                                                    where id=1''').fetchone())
            self.weapon[3] = loadings.load_image(self.weapon[3])
            self.weapon = Weapon(*self.weapon)
        self.mask = None
        self.hp = 100
        self.shooting = False
        self.weapon_clock = pygame.time.Clock()
        self.time_between_shoots = 0

    def rotate_image(self, pos):
        rel_x, rel_y = pos[0] - self.rect.x, pos[1] - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class MainHero(Character):
    def __init__(self, pos):
        super().__init__('hero')
        self.weapons = []
        self.load_weapon()
        self.slot_number = 0
        self.image = loadings.load_image('good_stay.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update_hero(self):
        if self.shooting:
            self.time_between_shoots += self.weapon_clock.tick()
            if self.time_between_shoots > 300:
                self.shoot(pygame.mouse.get_pos())
                self.time_between_shoots = 0
        else:
            self.time_between_shoots = 0
        next_x, next_y = 0, 0
        if pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 5
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 5
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 5
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 5
        if self.shooting:
            self.image = loadings.load_image('good_shoote.png')
        else:
            self.image = loadings.load_image('good_stay.png')
        self.rotate_image(pygame.mouse.get_pos())
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.rect.move(next_x, next_y)
        if pygame.sprite.spritecollideany(self, obstacles, collided=collide_with_mask) is not None:
            self.rect = self.rect.move(-next_x, -next_y)
        for bullet in enemy_bullets:
            if pygame.sprite.collide_mask(bullet, self):
                self.hp -= bullet.weapon.damage
                bullet.kill()
        if self.hp <= 0:
            lose()

    def load_weapon(self):
        for weap_id in data[1][0].split():
            self.weapons.append(Weapon(*loadings.load_weapon(weap_id)))

    def shoot(self, go_to):
        shot.play()
        delta_x = go_to[0] - self.rect.centerx
        delta_y = go_to[1] - self.rect.centery
        rad = math.sqrt(delta_x ** 2 + delta_y ** 2)
        rng = 0
        if hero.weapons[hero.slot_number].name == 'Machine-gun':
            rng = uniform(-0.2, 0.2)
        if delta_x and delta_y:
            bullet = Bullet(self.rect.centerx, self.rect.centery, hero.weapons[hero.slot_number], (delta_x / rad),
                            (delta_y / rad), rng)
            all_sprites.add(bullet)
            hero_bullets.add(bullet)


class Enemy(Character):
    def __init__(self, pos, n):
        super().__init__('enemy')
        self.image = loadings.load_image('bad_stay.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.check_shooting = pygame.USEREVENT + n + 2
        pygame.time.set_timer(self.check_shooting, 700)

    def update_enemy(self):
        delta_x = hero.rect.centerx - self.rect.centerx
        delta_y = hero.rect.centery - self.rect.centery
        if pygame.event.peek(self.check_shooting) and math.sqrt(delta_x ** 2 + delta_y ** 2) <= 600:
            pygame.event.get(self.check_shooting)
            self.check()
        if self.shooting:
            self.time_between_shoots += self.weapon_clock.tick()
            if self.time_between_shoots > 1000:
                self.shoot()
                self.time_between_shoots = 0
        else:
            self.time_between_shoots = 0
        if self.shooting:
            self.image = loadings.load_image('bad_shoot.png')
        else:
            self.image = loadings.load_image('bad_stay.png')
        self.rotate_image((hero.rect.x + hero.rect.w // 2, hero.rect.y + hero.rect.h // 2))
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        for bullet in hero_bullets:
            if pygame.sprite.collide_mask(bullet, self):
                self.hp -= bullet.weapon.damage
                bullet.kill()
        if self.hp <= 0:
            self.kill()

    def check(self):
        invis = InvisBullet(self.rect.center, self.weapon.radius)
        if invis.check_avail(hero.rect.center):
            self.shooting = True
        else:
            self.shooting = False
        invis.kill()

    def shoot(self):
        shot.play()
        delta_x = hero.rect.centerx - self.rect.centerx
        delta_y = hero.rect.centery - self.rect.centery
        rad = math.sqrt(delta_x ** 2 + delta_y ** 2)
        if delta_x and delta_y:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.weapon, delta_x / rad,
                            delta_y / rad, 0)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)


class Game:
    def __init__(self, in_room, in_hero):
        self.room = in_room
        self.hero = in_hero

    def render(self):
        self.hero.update_hero()
        for en in enemies:
            en.update_enemy()
        for bull in hero_bullets:
            bull.update()
        for bull in enemy_bullets:
            bull.update()
        self.room.render()
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        draw_hp(screen)
        invent.draw(screen)


def draw_hp(in_screen):
    pygame.draw.rect(in_screen, (204, 0, 0), (width // 4, height - 80, hero.hp * 2, 40))
    pygame.draw.rect(in_screen, (0, 0, 0), (width // 4, height - 80, 200, 40), 3)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        l_u_cell = all_cells.sprites()[0]
        r_d_cell = all_cells.sprites()[room.width * room.height - 1]
        if (l_u_cell.rect.x >= 0 and target.rect.x + target.rect.w // 2 < width // 2) or \
                (r_d_cell.rect.x <= width - r_d_cell.rect.w and width // 2 <= target.rect.x + target.rect.w // 2):
            self.dx = 0
        else:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)

        if (l_u_cell.rect.y >= 0 and target.rect.y + target.rect.h // 2 < height // 2) or \
                (r_d_cell.rect.y <= height - r_d_cell.rect.h and height // 2 <= target.rect.y + target.rect.h // 2):
            self.dy = 0
        else:
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


pygame.init()
pygame.mixer.music.load('music/kalinka.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(50)
FPS = 20
size = width, height = 1024, 768
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Back To USSR')
all_sprites = pygame.sprite.Group()
cells = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
hero_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
invent = pygame.sprite.Group()
all_cells = pygame.sprite.Group()
shot = pygame.mixer.Sound('music/shot.mp3')
put = pygame.mixer.Sound('music/put.mp3')
droped_weapon = []
data = loadings.load_results()
if not int(data[0][0]):
    start_titles()
    data[0][0] = int(data[0][0]) + 1
room = Room(data[0][0])
hero = MainHero((room.tile_width + 1, room.tile_height + 1))
game = Game(room, hero)
camera = Camera()
for i in range(5):
    enemy = Enemy((randrange(room.width * room.tile_width), randrange(room.height * room.tile_height)), i)
    while pygame.sprite.spritecollideany(enemy, obstacles, collided=collide_with_mask) or enemy.rect.colliderect(
            hero.rect):
        enemy.kill()
        enemy = Enemy((randrange(room.width * room.tile_width), randrange(room.height * room.tile_height)), i)
if int(data[0][0]) == 1:
    weap = Weapon(*loadings.load_weapon(2))
    weap.spr.kill()
    weap.drop(randrange(width), randrange(height))
    while pygame.sprite.spritecollideany(weap.sm_spr, obstacles):
        weap.sm_spr.kill()
        weap.drop(randrange(width), randrange(height))
pygame.display.flip()
hero.weapons[hero.slot_number].draw()
clock = pygame.time.Clock()


def run_game():
    hero.hp = 100
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                hero.shooting = True
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                hero.shooting = False
            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_q:
                    invent.remove(hero.weapons[hero.slot_number].spr)
                    if hero.slot_number < len(hero.weapons) - 1:
                        hero.slot_number += 1
                    else:
                        hero.slot_number = 0
                    hero.weapons[hero.slot_number].draw()
                if ev.key == pygame.K_g:
                    if hero.weapons[hero.slot_number].name != 'simple pistol':
                        hero.weapons[hero.slot_number].drop(hero.rect.centerx, hero.rect.centery)
                        del hero.weapons[hero.slot_number]
                        hero.slot_number -= 1
                        hero.weapons[hero.slot_number].draw()
                elif ev.key == pygame.K_f:
                    for i in range(len(droped_weapon)):
                        if droped_weapon[i][0].sm_spr.rect.x - hero.rect.x != 0 and \
                                droped_weapon[i][0].sm_spr.rect.y - hero.rect.y != 0:
                            square_go_x = math.fabs(droped_weapon[i][0].sm_spr.rect.x - hero.rect.x) ** 2
                            square_go_y = math.fabs(droped_weapon[i][0].sm_spr.rect.y - hero.rect.y) ** 2
                            go = math.sqrt(square_go_x + square_go_y)
                        else:
                            go = 15
                        if go <= 100:
                            put.play()
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
                                    hero.weapons[hero.slot_number].drop(hero.rect.centerx, hero.rect.centery)
                                    hero.weapons[hero.slot_number] = droped_weapon[i][0]
                                    all_sprites.add(droped_weapon[i][0].sm_spr)
                                    del droped_weapon[i]
                            break

        camera.update(hero)
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)


run_game()
