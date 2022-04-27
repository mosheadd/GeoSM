import pygame
from random import randrange
import sys
import os


class SnakeGame:
    def __init__(self):
        self.RES = 760
        self.SIZE = 40

        self.x, self.y = randrange(0, self.RES, self.SIZE), randrange(0, self.RES, self.SIZE)
        self.apple = randrange(0, self.RES, self.SIZE), randrange(0, self.RES, self.SIZE)
        self.dirs = {'W': True, 'A': True, 'S': True, 'D': True}
        self.lenght = 1
        self.snake = [(x, y)]
        self.dx, self.dy = 0, 0
        self.score = 0
        self.fps = 8
        self.hs = [0]

        pygame.init()
        self.sc = pygame.display.set_mode([self.RES, self.RES])
        self.clock = pygame.time.Clock()
        self.font_score = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_end = pygame.font.SysFont('Arial', 69, bold=True)
        self.font_hs = pygame.font.SysFont('Arial', 26, bold=True)
        self.img = pygame.image.load('fon.png').convert()

    def load_image(self, name):
        fullname = os.path.join(name)
        image = pygame.image.load(fullname)
        image = image.convert_alpha()
        return image

    def start_screen(self, width, height):
        self.intro = ['Выберите цвет змейки', 'Зеленый', 'Синий', 'Желтый']
        self.fonts = []
        self.background = pygame.transform.scale(self.load_image('fon.png'), (width, height))
        self.sc.blit(self.background, (0, 0))
        y = 5
        for line in self.intro:
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
            self.fonts.append(s)
            self.sc.blit(s, (rect.x, rect.y))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    y = 5
                    for i in range(len(self.fonts)):
                        rect = self.fonts[i].get_rect()
                        rect.x = width // 2 - rect.w // 2
                        rect.y = y
                        if rect.collidepoint(pygame.mouse.get_pos()) and i != 0:
                            if self.intro[i] == 'Зеленый':
                                return 1
                            if self.intro[i] == 'Синий':
                                return 2
                            if self.intro[i] == 'Желтый':
                                return 3
                        y += height // 4
            # screen.blit(background, (0, 0))
            for i in range(len(self.intro)):
                if self.fonts[i].get_rect().collidepoint(pygame.mouse.get_pos()):
                    color = (255, 10, 10)
                else:
                    color = (250, 250, 210)
                rect = self.fonts[i].get_rect()
                x = width // 2 - rect.w // 2
                self.sc.blit(self.fonts[i], (x, y))
                pygame.display.flip()
                y += height // 4
            pygame.display.flip()
            self.clock.tick(self.fps)

    def game(self, qwer, hs):
        self.sc.blit(self.img, (0, 0))
        # drawing snake
        if qwer == 1:
            col = 'green'
        if qwer == 2:
            col = 'blue'
        if qwer == 3:
            col = 'yellow'
        [(pygame.draw.rect(self.sc, pygame.Color(col), (i, j, self.SIZE - 2, self.SIZE - 2))) for i, j in self.snake]
        pygame.draw.rect(self.sc, pygame.Color('red'), (*self.apple, self.SIZE, self.SIZE))
        # show score
        render_score = self.font_score.render(f'Score: {self.score}', 1, pygame.Color('orange'))
        self.sc.blit(render_score, (5, 5))
        # snake movement
        self.x += self.dx * self.SIZE
        self.y += self.dy * self.SIZE
        self.snake.append((self.x, self.y))
        snake = self.snake[-self.lenght:]
        # eating apple
        if snake[-1] == self.apple:
            apple = randrange(0, self.RES, self.SIZE), randrange(0, self.RES, self.SIZE)
            self.lenght += 1
            self.score += 1
            self.fps += 1
        # game over
        if self.x < 0 or self.x > self.RES - self.SIZE or self.y < 0 or self.y > self.RES - self.SIZE or len(
                snake) != len(set(self.snake)):
            while True:
                render_end = self.font_end.render('GAME OVER', 1, pygame.Color('red'))
                render_score = self.font_score.render(f'Score: {str(self.score)}', 1, pygame.Color('blue'))
                render_hs = self.font_hs.render(f'Hight score: {str(hs)}', 1, pygame.Color('blue'))
                self.sc.blit(render_end, (self.RES // 2 - 200, self.RES // 3))
                self.sc.blit(render_score, (self.RES // 2 - 200, self.RES // 4))
                self.sc.blit(render_hs, (self.RES // 2 + 50, self.RES // 4))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()

        pygame.display.flip()
        self.clock.tick(self.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        # control
        key = pygame.key.get_pressed()
        if key[pygame.K_w] and self.dirs['W']:
            self.dx, self.dy = 0, -1
            self.dirs = {'W': True, 'A': True, 'S': False, 'D': True}

        if key[pygame.K_s] and self.dirs['S']:
            self.dx, self.dy = 0, 1
            self.dirs = {'W': False, 'A': True, 'S': True, 'D': True}

        if key[pygame.K_a] and self.dirs['A']:
            self.dx, self.dy = -1, 0
            self.dirs = {'W': True, 'A': True, 'S': True, 'D': False}

        if key[pygame.K_d] and self.dirs['D']:
            self.dx, self.dy = 1, 0
            self.dirs = {'W': True, 'A': False, 'S': True, 'D': True}
        return self.score

    def starting_game(self):
        while True:
            diff = self.start_screen(self.RES, self.RES)
            if diff == 1 or diff == 2 or diff == 3:
                while True:
                    self.game(diff)
