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

    def render(self):
        center = self.pos[0] * room.tile_width + room.tile_width // 2, self.pos[
            1] * room.tile_height + room.tile_height // 2
        pygame.draw.circle(screen, (255, 255, 255), center, room.tile_width // 2)


class Game:
    def __init__(self, room, hero):
        self.room = room
        self.hero = hero

    def render(self):
        self.room.render()
        self.hero.render()

    def update_hero(self):
        next_x, next_y = self.hero.pos
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
            self.hero.side = 'left'
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
            self.hero.side = 'right'
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
            self.hero.side = 'up'
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
            self.hero.side = 'down'
        if self.room.is_free((next_x, next_y)):
            self.hero.pos = (next_x, next_y)


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
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
