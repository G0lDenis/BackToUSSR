import pygame
import sys
import pygame_widgets as pw
import os


def terminate():
    pygame.quit()
    sys.exit()

def run_game():
    os.startfile(r'main.py')


pygame.font.init()
size = width, height = 1024, 768
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Back To USSR')
img = pygame.image.load("Images\menu_back.jpg")
font = pygame.font.SysFont('tahoma', 36)
button_play = pw.Button(
    screen, 80, 300, 300, 50, text='Играть',
    fontSize=50,
    inactiveColour=(180, 0, 1),
    pressedColour=(180, 0, 1),
    onClick=lambda: run_game(),
    textColour=(255, 214, 3),
    hoverColour=(160, 0, 1),
    font=font,
    textHAlign='centre'
)
button_settings = pw.Button(
    screen, 820, 300, 300, 50, text='Настройки',
    fontSize=50,
    inactiveColour=(180, 0, 1),
    pressedColour=(180, 0, 1),
    onClick=lambda: settings(),
    textColour=(255, 214, 3),
    hoverColour=(160, 0, 1),
    font=font,
    textHAlign='centre'
)


def show_btn():
    show = True
    while show:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                show = False
        screen.blit(img, (0, 0))
        button_play.listen(events)
        button_play.draw()
        button_settings.listen(events)
        button_settings.draw()
        pygame.display.update()


show_btn()
