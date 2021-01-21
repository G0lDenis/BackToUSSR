import pygame

pygame.init()




SIZE = WIDTH, HEIGHT = (1024, 768)
screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)


def blit_text(surface, text, pos, font, color=(10, 255, 2)):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height


text = 'Сибирь. 2048 год. Прибывает майор ФСБ. ' \
       'Во время поиска нефтяных месторождений ' \
       'обнаружили скрытый от глаз город. СССР ' \
       'опережающие время научные исследования. ' \
       'В 90-е Союз развалился, исследования ' \
       'прекратились, архивы покрылись метровым ' \
       'слоем пыли, но остались ОНИ. Киборги. ' \
       'Они запрограммированы на то, чтобы уста' \
       'новить коммунизм на всем земном шаре. ' \
       'Они верны своей цели и не остановятся ' \
       'ни перед чем. Коммунизм строили к 80-ому ' \
       'году - не построили, и решили навязать ' \
       'его огнём и кровью. Повезло, что исследо' \
       'вания забросили, но, когда нашли это мес' \
       'то – этот город, система запустилась и ' \
       'вряд ли уже возможно их остановить. Они ' \
       'вскрыли титановую дверь, за которой их ' \
       'оставили, изнутри сбежали. Их не удалось ' \
       'обнаружить. В 100 км отсюда аэродром, они ' \
       'об этом знают. Они захватят летательный ' \
       'аппарат и улетят. Дальше их будет не ус' \
       'транить. Они сделаны по образу и подобию ' \
       'человека. И убить их можно как человека. ' \
       'Одна проблема - но они быстрее, сильнее и ' \
       'умнее, чем человек. Они ушли 3-4 часа назад. ' \
       'У вас чуть меньше этого. Удачи!'

font = pygame.font.SysFont("Times New Roman", 35, bold=True)

ev = pygame.USEREVENT + 20
pygame.time.set_timer(ev, 20000)


def start_titles():
    global go
    go = True
    while go:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == ev:
                go = False
        if go:
            screen.fill((0, 0, 0))
            blit_text(screen, text, (20, 20), font)
            pygame.display.update()
