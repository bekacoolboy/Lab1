import pygame
import random

pygame.init()

# окно
WIDTH = 600
HEIGHT = 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

# цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# параметры змейки
snake_size = 15
snake_speed = 10

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(win, GREEN, [x[0], x[1], snake_size, snake_size])

def game_loop():
    game_over = False
    game_close = False

    x = WIDTH // 2
    y = HEIGHT // 2
    dx = 0
    dy = 0

    snake_list = []
    length = 1

    food_x = round(random.randrange(0, WIDTH - snake_size) / snake_size) * snake_size
    food_y = round(random.randrange(0, HEIGHT - snake_size) / snake_size) * snake_size

    while not game_over:
        while game_close:
            win.fill(BLACK)
            msg = font.render("Игра окончена! Нажми C — продолжить или Q — выход", True, RED)
            win.blit(msg, [20, HEIGHT//2 - 20])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx = -snake_size
                    dy = 0
                elif event.key == pygame.K_RIGHT:
                    dx = snake_size
                    dy = 0
                elif event.key == pygame.K_UP:
                    dy = -snake_size
                    dx = 0
                elif event.key == pygame.K_DOWN:
                    dy = snake_size
                    dx = 0

        x += dx
        y += dy

        # выход за границы
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        win.fill(BLACK)
        pygame.draw.rect(win, RED, [food_x, food_y, snake_size, snake_size])

        snake_head = []
        snake_head.append(x)
        snake_head.append(y)
        snake_list.append(snake_head)

        if len(snake_list) > length:
            del snake_list[0]

        # столкновение с собой
        for part in snake_list[:-1]:
            if part == snake_head:
                game_close = True

        draw_snake(snake_list)

        pygame.display.update()

        # еда
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - snake_size) / snake_size) * snake_size
            food_y = round(random.randrange(0, HEIGHT - snake_size) / snake_size) * snake_size
            length += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

game_loop()
