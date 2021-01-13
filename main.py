import pygame
import sys
import loadings


def terminate():
    pygame.quit()
    sys.exit()


class MainMenu:
    pass


class Room:
    def __init__(self, name, free_tiles):
        self.map = loadings.load_map(name)
        self.width = self.map.width
        self.height = self.map.height
        self.tile_width = self.map.tilewidth
        self.tile_height = self.map.tileheight
        self.free_tiles = free_tiles

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                im = self.map.get_tile_image(x, y, 0)
                screen.blit(im, (x * self.tile_width, y * self.tile_height))

    def get_tile_id(self, pos):
        return self.map.tiledgidmap[self.map.get_tile_gid(*pos, 0)]

    def is_free(self, pos):
        return self.in_field(pos) and self.get_tile_id(pos) in self.free_tiles

    def in_field(self, pos):
        if 0 <= pos[0] <= self.width - 1 and 0 <= pos[1] <= self.height - 1:
            return True
        return False


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
        all_sprites.add(self)
        self.moving = False

    def render(self):
        rect_coord = self.pos[0] * room.tile_width, self.pos[
            1] * room.tile_height
        if self.side == 'right':
            angle = 0
        elif self.side == 'left':
            angle = -180
        elif self.side == 'up':
            angle = -90
        else:
            angle = 90
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        else:
            self.cur_frame = 0
        self.image = pygame.transform.rotate(self.frames[self.cur_frame], angle)
        self.image.set_colorkey((255, 255, 255))
        self.rect = pygame.Rect(*rect_coord, self.image.get_width(), self.image.get_height())
        self.moving = False

    def cut_sheet(self, sheet):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 3,
                                sheet.get_height())
        for j in range(3):
            frame_location = (self.rect.w * j, 0)
            print(frame_location, self.rect.size)
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))


class Game:
    def __init__(self, room, hero):
        self.room = room
        self.hero = hero

    def render(self):
        self.room.render()
        self.hero.render()
        all_sprites.draw(screen)

    def update_hero(self):
        next_x, next_y = self.hero.pos
        if pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 1
            self.hero.side = 'left'
            self.hero.moving = True
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 1
            self.hero.side = 'right'
            self.hero.moving = True
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 1
            self.hero.side = 'up'
            self.hero.moving = True
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 1
            self.hero.side = 'down'
            self.hero.moving = True
        if self.room.is_free((next_x, next_y)):
            self.hero.pos = (next_x, next_y)


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    all_sprites = pygame.sprite.Group()
    room = Room('f-r.tmx', [1])
    hero = MainHero((0, 3))
    game = Game(room, hero)
    pygame.display.flip()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
        game.update_hero()
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
