import sys
import pygame
import pygame_widgets as pw
from subprocess import call


def terminate():
    pygame.quit()
    sys.exit()


pygame.font.init()
size = width, height = 1024, 768
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Back To USSR')
img = pygame.image.load("images\menu_back.jpg")
img = pygame.transform.scale(img, (1024, 768))
font = pygame.font.SysFont('tahoma', 36)
button_play = pw.Button(
    screen, 340, 220, 300, 50, text='Играть',
    fontSize=50,
    inactiveColour=(180, 0, 1),
    pressedColour=(180, 0, 1),
    onClick=lambda: call(["python", "main.py"]),
    textColour=(255, 214, 3),
    hoverColour=(160, 0, 1),
    font=font,
    textHAlign='centre'
)
button_settings = pw.Button(
    screen, 340, 400, 300, 50, text='Настройки',
    fontSize=50,
    inactiveColour=(180, 0, 1),
    pressedColour=(180, 0, 1),
    onClick=lambda: print('В дальнейшем здесь будут настройки'),
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
