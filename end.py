import sys
import pygame
import pygame_widgets as pw
from subprocess import call
import time


def terminate():
    pygame.quit()
    sys.exit()


def lose():
    global button_restart, img, screen
    pygame.font.init()
    size = width, height = 1024, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Back To USSR')
    img = pygame.image.load("images\end_game.jpg")
    img = pygame.transform.scale(img, (1024, 768))
    font = pygame.font.SysFont('tahoma', 36)
    button_restart = pw.Button(
        screen, 340, 400, 300, 50, text='Снова в бой!',
        fontSize=50,
        inactiveColour=(180, 0, 1),
        pressedColour=(180, 0, 1),
        onClick=lambda: restart(),
        textColour=(255, 214, 3),
        hoverColour=(160, 0, 1),
        font=font,
        textHAlign='centre'
    )
    show_btn()


def show_btn():
    show = True
    while show:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                show = False
        screen.blit(img, (0, 0))
        button_restart.listen(events)
        button_restart.draw()
        pygame.display.update()


def restart():
    terminate()
    call(["python", "main.py"])
    pygame.quit()
