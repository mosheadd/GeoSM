import pygame
from random import randrange
import sys
import os

RES = 760
SIZE = 40

x, y = randrange(0, RES, SIZE), randrange(0, RES, SIZE)
apple = randrange(0, RES, SIZE), randrange(0, RES, SIZE)
dirs = {'W': True, 'A': True, 'S': True, 'D': True}
lenght = 1
snake = [(x, y)]
dx, dy = 0, 0
score = 0
fps = 8
hs = [0]

pygame.init()
sc = pygame.display.set_mode([RES, RES])
clock = pygame.time.Clock()
font_score = pygame.font.SysFont('Arial', 26, bold=True)
font_end = pygame.font.SysFont('Arial', 69, bold=True)
font_hs = pygame.font.SysFont('Arial', 26, bold=True)
img = pygame.image.load('fon.png').convert()


def load_image(name):
    fullname = os.path.join(name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    return image


def start_screen(width, height):
    intro = ['Выберите цвет змейки', 'Зеленый', 'Синий', 'Желтый']
    fonts = []
    background = pygame.transform.scale(load_image('fon.png'), (width, height))
    sc.blit(background, (0, 0))
    y = 5
    for line in intro:
        if line == 'Зеленый':
            s = pygame.font.Font(None, 70).render(line, True, (0, 250, 0))
        elif line == 'Синий':
            s = pygame.font.Font(None, 70).render(line, True, (0, 0, 250))
        elif line == 'Желтый':
            s = pygame.font.Font(None, 70).render(line, True, 'yellow')
        else:
            s = pygame.font.Font(None, 70).render(line, True, (250, 250, 210))
        rect = s.get_rect()
        rect.x = width // 2 - rect.w // 2
        rect.y = y
        y += height // 4
        fonts.append(s)
        sc.blit(s, (rect.x, rect.y))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                y = 5
                for i in range(len(fonts)):
                    rect = fonts[i].get_rect()
                    rect.x = width // 2 - rect.w // 2
                    rect.y = y
                    if rect.collidepoint(pygame.mouse.get_pos()) and i != 0:
                        if intro[i] == 'Зеленый':
                            return 1
                        if intro[i] == 'Синий':
                            return 2
                        if intro[i] == 'Желтый':
                            return 3
                    y += height // 4
        # screen.blit(background, (0, 0))
        for i in range(len(intro)):
            if fonts[i].get_rect().collidepoint(pygame.mouse.get_pos()):
                color = (255, 10, 10)
            else:
                color = (250, 250, 210)
            rect = fonts[i].get_rect()
            x = width // 2 - rect.w // 2
            sc.blit(fonts[i], (x, y))
            pygame.display.flip()
            y += height // 4
        pygame.display.flip()
        clock.tick(fps)


def game(qwer):
    global apple, score, snake, x, dx, y, dy, lenght, fps, dirs, hs
    sc.blit(img, (0, 0))
    # drawing snake
    if qwer == 1:
        col = 'green'
    if qwer == 2:
        col = 'blue'
    if qwer == 3:
        col = 'yellow'
    [(pygame.draw.rect(sc, pygame.Color(col), (i, j, SIZE - 2, SIZE - 2))) for i, j in snake]
    pygame.draw.rect(sc, pygame.Color('red'), (*apple, SIZE, SIZE))
    # show score
    render_score = font_score.render(f'Score: {score}', 1, pygame.Color('orange'))
    sc.blit(render_score, (5, 5))
    # snake movement
    x += dx * SIZE
    y += dy * SIZE
    snake.append((x, y))
    snake = snake[-lenght:]
    # eating apple
    if snake[-1] == apple:
        apple = randrange(0, RES, SIZE), randrange(0, RES, SIZE)
        lenght += 1
        score += 1
        fps += 1
    # game over
    if x < 0 or x > RES - SIZE or y < 0 or y > RES - SIZE or len(snake) != len(set(snake)):
        while True:
            if score > hs[-1]:
                hs.append(score)
            render_end = font_end.render('GAME OVER', 1, pygame.Color('red'))
            render_score = font_score.render(f'Score: {str(score)}', 1, pygame.Color('blue'))
            render_hs = font_hs.render(f'Hight score: {str(hs[-1])}', 1, pygame.Color('blue'))
            sc.blit(render_end, (RES // 2 - 200, RES // 3))
            sc.blit(render_score, (RES // 2 - 200, RES // 4))
            sc.blit(render_hs, (RES // 2 + 50, RES // 4))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

    pygame.display.flip()
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    # control
    key = pygame.key.get_pressed()
    if key[pygame.K_w] and dirs['W']:
        dx, dy = 0, -1
        dirs = {'W': True, 'A': True, 'S': False, 'D': True}

    if key[pygame.K_s] and dirs['S']:
        dx, dy = 0, 1
        dirs = {'W': False, 'A': True, 'S': True, 'D': True}

    if key[pygame.K_a] and dirs['A']:
        dx, dy = -1, 0
        dirs = {'W': True, 'A': True, 'S': True, 'D': False}

    if key[pygame.K_d] and dirs['D']:
        dx, dy = 1, 0
        dirs = {'W': True, 'A': False, 'S': True, 'D': True}

while True:
    diff = start_screen(RES, RES)
    if diff == 1 or diff == 2 or diff == 3:
        while True:
            game(diff)
