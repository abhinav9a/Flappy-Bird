import pygame
from random import randint, choice
from pygame.locals import *
import sys


def create_pipes():
    random_pipe_height = choice(pipe_height)
    down_pipe = pipe.get_rect(midtop=(WIDTH + 100, random_pipe_height))
    up_pipe = pipe.get_rect(midbottom=(WIDTH + 100, random_pipe_height - 150))
    return down_pipe, up_pipe


def move_pipes(pipes):
    for pipe_rect in pipes:
        pipe_rect.centerx -= 1
    return pipes


def draw_pipes(pipes):
    for pipe_rect in pipes:
        if pipe_rect.bottom > HEIGHT:
            screen.blit(pipe, pipe_rect)
        else:
            flipped_pipe = pygame.transform.flip(pipe, False, True)
            screen.blit(flipped_pipe, pipe_rect)


def base_animation():
    global base_pos
    base_pos -= 1
    screen.blit(base, (base_pos, 450))
    screen.blit(base, (base_pos + WIDTH, 450))
    if base_pos <= -WIDTH:
        base_pos = 0


def bird_animation(birds):
    new_flappy = pygame.transform.rotozoom(birds[flap_index], -flappy_y * 5, 1)
    new_flappy_rect = flappy.get_rect(center=(WIDTH / 4, flappy_rect.centery))
    return new_flappy, new_flappy_rect


def check_collision(pipes):
    for pipe_rect in pipes:
        if flappy_rect.colliderect(pipe_rect):
            hit_audio.play()
            return False
    if (flappy_rect.top <= -200) or (flappy_rect.bottom >= 460):
        hit_audio.play()
        return False

    return True


def display_score():
    game_score = game_font.render(f'Score: {int(score)}', True, WHITE)
    screen.blit(game_score, (2 * WIDTH / 5, 25))


def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


# Variables
WIDTH = 288
HEIGHT = 512
WHITE = (255, 255, 255)
FPS = 120

flap_index = 0
base_pos = 0
flappy_y = 0
rate = 0.15

# Score
score = 0
high_score = 0
score_sound_countdown = FPS

# Images
bg_images = ['assets/images/background-day.png', 'assets/images/background-night.png']
flappy_img = [['assets/images/bluebird-downflap.png', 'assets/images/bluebird-midflap.png',
               'assets/images/bluebird-upflap.png'],
              ['assets/images/redbird-downflap.png', 'assets/images/redbird-midflap.png',
               'assets/images/redbird-upflap.png'],
              ['assets/images/yellowbird-downflap.png', 'assets/images/yellowbird-midflap.png',
               'assets/images/yellowbird-upflap.png']
              ]
pipes_img = ['assets/images/pipe-red.png', 'assets/images/pipe-green.png']

# Initialise pygame and mixer
pygame.mixer.pre_init(channels=1, buffer=512)
pygame.init()

# Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load('flappy.ico')
pygame.display.set_icon(icon)
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

# Font
game_font = pygame.font.Font('assets/font.ttf', 21)

# Sounds
swoosh_audio = pygame.mixer.Sound('assets/audio/point.wav')
hit_audio = pygame.mixer.Sound('assets/audio/hit.wav')
wing_audio = pygame.mixer.Sound('assets/audio/wing.wav')

# Load images
bg = pygame.image.load(bg_images[randint(0, 1)]).convert()
base = pygame.image.load('assets/images/base.png').convert()
game_over_img = pygame.image.load('assets/images/message.png')

# Load Pipes
pipe = pygame.image.load(pipes_img[randint(0, 1)]).convert()
pipe_rect_list = []
pipe_height = [200, 300, 400]

# Load Bird
flappy_list = []
flappy_img = flappy_img[randint(0, 2)]
for i in range(3):
    flappy_list.append(pygame.image.load(flappy_img[i]).convert_alpha())
flappy = flappy_list[flap_index]
flappy_rect = flappy.get_rect(center=(WIDTH / 4, HEIGHT / 2))  # Draw Rect around bird

# User Events
FLAPPY_WING = pygame.USEREVENT
pygame.time.set_timer(FLAPPY_WING, FPS)
PIPE_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(PIPE_SPAWN, 1500)

# ******************************************** GAME LOOP ******************************************
game_active = True
running = True
while running:
    clock.tick(FPS)
    # **************************** EVENT LOOP START *****************************************
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                wing_audio.play()
                flappy_y = -4

            # Restart Game
            if (event.key == K_SPACE) and not game_active:
                # print(f'Before: {game_active}')
                game_active = True
                pipe_rect_list.clear()
                flappy_rect.center = (WIDTH / 4, HEIGHT / 2)
                flappy_y = 0
                score = 0
                # print(f'After: {game_active}')

        # Bird Animation
        if event.type == FLAPPY_WING:
            if flap_index < 2:
                flap_index += 1
            else:
                flap_index = 0
            flappy, flappy_rect = bird_animation(flappy_list)

        # Spawn Pipes
        if event.type == PIPE_SPAWN:
            pipe_rect_list.extend(create_pipes())
    # ***************************** EVENT LOOP END ******************************************

    screen.blit(bg, (0, 0))
    if game_active:
        # ************************************* Game Screen *********************************************
        # Bird Movement
        flappy_y += rate
        flappy_rect.centery += flappy_y
        screen.blit(flappy, flappy_rect)

        # Pipes
        pipe_rect_list = move_pipes(pipe_rect_list)
        draw_pipes(pipe_rect_list)

        # Score
        score += 1 / FPS
        score_sound_countdown -= 1
        if score_sound_countdown == 0:
            swoosh_audio.play()
            score_sound_countdown = FPS

        # Collision
        game_active = check_collision(pipe_rect_list)
    else:
        # **********************************  Game Over Screen ******************************************
        high_score = update_high_score(score, high_score)
        game_high_score = game_font.render(f"High score: {int(high_score)}", True, WHITE)
        screen.blit(game_high_score, (100, 0.75 * HEIGHT))
        screen.blit(game_over_img, (WIDTH / 5, 75))

    base_animation()
    display_score()

    pygame.display.update()
