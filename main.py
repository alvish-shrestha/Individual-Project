import pygame
import json
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gamified Language Acquisition")

# Fonts
FONT = pygame.font.SysFont("Arial", 28)
BIG_FONT = pygame.font.SysFont("Arial", 40)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Load level data
with open("data/levels.json") as f:
    levels = json.load(f)["levels"]

# Load sounds
correct_sound = pygame.mixer.Sound("assets/sounds/correct.mp3")
wrong_sound = pygame.mixer.Sound("assets/sounds/wrong.mp3")

# Game variables
score = 0
current_question = 0
time_limit = 10  # seconds
timer_event = USEREVENT + 1

def draw_text(text, font, color, x, y):
    rendered = font.render(text, True, color)
    screen.blit(rendered, (x, y))

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Gamified Language Learning", BIG_FONT, BLACK, 150, 200)
        draw_text("Press SPACE to Start", FONT, BLACK, 250, 300)
        draw_text("Press ESC to Exit", FONT, BLACK, 260, 350)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    game_loop()
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def game_loop():
    global score, current_question

    level = levels[0]  # Canteen scene
    question_data = level["questions"][current_question]

    # Load and resize images
    background = pygame.image.load(level["background"])

    question_image = pygame.image.load(question_data["image"])
    question_image = pygame.transform.scale(question_image, (200, 200))  # adjust size

    # Timer setup
    pygame.time.set_timer(timer_event, 1000)
    time_left = time_limit

    selected_option = None
    feedback = ""

    running = True
    while running:
        screen.blit(background, (0,0))
        screen.blit(question_image, (300, 150))
        draw_text(question_data["question"], FONT, BLACK, 200, 50)

        # Draw options
        for i, option in enumerate(question_data["options"]):
            color = BLACK
            if selected_option == i:
                color = GREEN if option == question_data["answer"] else RED
            draw_text(f"{i+1}. {option}", FONT, color, 250, 400 + i*40)

        draw_text(f"Score: {score}", FONT, BLACK, 650, 20)
        draw_text(f"Time Left: {time_left}s", FONT, BLACK, 50, 20)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key in [K_1, K_2, K_3, K_4]:
                    selected_option = event.key - K_1
                    chosen = question_data["options"][selected_option]
                    if chosen == question_data["answer"]:
                        score += 10
                        feedback = "Correct!"
                        correct_sound.play()
                    else:
                        feedback = "Wrong!"
                        wrong_sound.play()
            if event.type == timer_event:
                time_left -= 1
                if time_left <= 0:
                    feedback = f"Time's up! Answer: {question_data['answer']}"
                    running = False

        if selected_option is not None:
            pygame.time.delay(1000)  # Show feedback
            running = False

    # Next question or end
    current_question += 1
    if current_question < len(level["questions"]):
        game_loop()
    else:
        end_screen()

def end_screen():
    screen.fill(WHITE)
    draw_text("Game Over!", BIG_FONT, BLACK, 300, 200)
    draw_text(f"Your Score: {score}", FONT, BLACK, 320, 300)
    draw_text("Press ESC to Exit", FONT, BLACK, 270, 400)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main_menu()
