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
        self.tile_width = 32
        self.tile_height = 32
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


class MainHero(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.side = 'right'
        self.cur_frame = 0
        self.frames = []
        self.cut_sheet(loadings.load_image('main_hero_sp.png'))
        self.moving = False
        all_sprites.add(self)

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
        self.rotate_image(pygame.mouse.get_pos())
        self.image.set_colorkey((255, 255, 255))
        self.moving = False

    def in_field(self):
        pass

    def rotate_image(self, pos):
        pass


class Game:
    def __init__(self, room, hero):
        self.room = room
        self.hero = hero

    def render(self):
        self.hero.update_hero()
        self.room.render()
        all_sprites.draw(screen)


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    room = Room('f-r.txt')
    hero = MainHero((0, 3 * room.tile_height))
    game = Game(room, hero)
    pygame.display.flip()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
