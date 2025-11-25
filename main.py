import pygame
import speech_recognition as sr
import random
import os
import math

pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EngageEnglish: Gamified Speaking Adventure")

# Colors
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
LIGHT_GRAY = (200, 200, 200)
BLUE1 = (83, 144, 217)
BLUE2 = (32, 64, 128)
YELLOW = (255, 215, 0)
GREEN = (0, 200, 0)
RED = (255, 70, 70)
TRANSPARENT_WHITE = (255, 255, 255, 40)
SHADOW_COLOR = (0, 0, 0, 100)

# Fonts
font_small = pygame.font.Font(None, 28)
font_medium = pygame.font.Font(None, 44)
font_large = pygame.font.Font(None, 74)

# Load images helper
def load_img(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

def load_sentences(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

assets_path = "assets/images"
canteen_img = load_img(os.path.join(assets_path, "canteen.png"), (450, 300))
mic_img = load_img(os.path.join(assets_path, "mic.png"), (70, 70))
correct_img = load_img(os.path.join(assets_path, "correct.png"), (45, 45))
wrong_img = load_img(os.path.join(assets_path, "incorrect.png"), (45, 45))

# Speech recognition setup
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Load sentences and pick initial random sentence
sentences = load_sentences("sentences.txt")
current_sentence = random.choice(sentences)

# Game variables
points = 0
feedback = ""
feedback_icon = None
feedback_color = WHITE
listening = False
game_over = False

# Timing for animations
mic_pulse_time = 0
feedback_alpha = 0
feedback_fade_in = False

def draw_gradient(surface, color1, color2):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = (
            int(color1[0] * (1 - ratio) + color2[0] * ratio),
            int(color1[1] * (1 - ratio) + color2[1] * ratio),
            int(color1[2] * (1 - ratio) + color2[2] * ratio)
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

def draw_rounded_rect(surface, color, rect, radius=20):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_shadow_rect(surface, rect, radius=20, shadow_color=(0,0,0,100), offset=(5,5)):
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, shadow_color, shadow_surface.get_rect(), border_radius=radius)
    surface.blit(shadow_surface, (rect.x + offset[0], rect.y + offset[1]))

def draw_text(text, font, color, x, y, center=True, shadow=True):
    if shadow:
        # Draw shadow
        shadow_surf = font.render(text, True, BLACK)
        if center:
            shadow_rect = shadow_surf.get_rect(center=(x+2, y+2))
        else:
            shadow_rect = shadow_surf.get_rect(topleft=(x+2, y+2))
        screen.blit(shadow_surf, shadow_rect)

    txt = font.render(text, True, color)
    if center:
        rect = txt.get_rect(center=(x, y))
        screen.blit(txt, rect)
    else:
        screen.blit(txt, (x, y))

def get_speech_input():
    global feedback, feedback_color, feedback_icon, listening
    listening = True
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        result = recognizer.recognize_google(audio)
        listening = False
        return result.lower()
    except sr.WaitTimeoutError:
        feedback = "⌛ Timeout! Try speaking faster."
        feedback_color = RED
        feedback_icon = wrong_img
    except sr.UnknownValueError:
        feedback = "❌ Couldn't recognize. Try again!"
        feedback_color = RED
        feedback_icon = wrong_img
    except sr.RequestError:
        feedback = "⚠️ API unavailable. Check internet."
        feedback_color = RED
        feedback_icon = wrong_img
    listening = False
    return ""

def draw_mic_button(x, y, base_img, pulse_time, listening):
    # Pulse animation on mic icon when listening
    scale = 1.0
    if listening:
        scale = 1 + 0.1 * math.sin(pulse_time * 5)
    scaled_img = pygame.transform.rotozoom(base_img, 0, scale)
    rect = scaled_img.get_rect(center=(x, y))
    screen.blit(scaled_img, rect)

def main():
    global points, feedback, feedback_icon, feedback_color, listening, game_over, current_sentence
    global mic_pulse_time, feedback_alpha, feedback_fade_in

    clock = pygame.time.Clock()
    particles = []

    while True:
        dt = clock.tick(60) / 1000.0
        mic_pulse_time += dt

        draw_gradient(screen, BLUE1, BLUE2)

        # Floating dots animation
        if len(particles) < 50:
            particles.append([random.randint(0, WIDTH), 0])
        for p in particles[:]:
            pygame.draw.circle(screen, WHITE, p, 2)
            p[1] += 50 * dt
            if p[1] > HEIGHT:
                particles.remove(p)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not listening and not game_over:
                    if event.key == pygame.K_SPACE:
                        user = get_speech_input()
                        if user:
                            target = current_sentence.lower()
                            if user == target:
                                feedback = "✅ Perfect!"
                                feedback_color = GREEN
                                feedback_icon = correct_img
                                points += 50
                                # Pick a new random sentence
                                current_sentence = random.choice(sentences)
                            else:
                                feedback = f"❌ You said: '{user}'"
                                feedback_color = RED
                                feedback_icon = wrong_img

                            feedback_alpha = 0
                            feedback_fade_in = True
                elif game_over and event.key == pygame.K_r:
                    points = 0
                    feedback = ""
                    feedback_icon = None
                    feedback_color = WHITE
                    game_over = False
                    current_sentence = random.choice(sentences)

        # Fade in feedback text and icon
        if feedback_fade_in and feedback_alpha < 255:
            feedback_alpha += 5
        elif feedback_alpha >= 255:
            feedback_fade_in = False

        # Main UI Drawing
        if not game_over:
            # Title with drop shadow
            draw_text("EngageEnglish", font_large, YELLOW, WIDTH//2, 60)

            # Points display with shadow
            draw_text(f"Points: {points}", font_medium, WHITE, WIDTH - 160, 40, center=False)

            # Panel with shadow (glass effect simulation)
            panel_rect = pygame.Rect(180, 150, 540, 400)
            draw_shadow_rect(screen, panel_rect, radius=30, shadow_color=SHADOW_COLOR)
            panel_surf = pygame.Surface((540, 400), pygame.SRCALPHA)
            panel_surf.fill((255, 255, 255, 50))  # frosted glass effect
            screen.blit(panel_surf, panel_rect.topleft)
            draw_rounded_rect(screen, (255, 255, 255, 60), panel_rect, 30)

            # Image
            screen.blit(canteen_img, (225, 180))

            # Instruction text
            draw_text("Say this sentence:", font_medium, WHITE, WIDTH//2, 480)
            draw_text(f"\"{current_sentence}\"", font_medium, YELLOW, WIDTH//2, 520)

            # Mic button with pulse animation
            draw_mic_button(WIDTH//2, 580, mic_img, mic_pulse_time, listening)

            draw_text("Press SPACE to speak", font_small, LIGHT_GRAY, WIDTH//2, 630)

            # Listening indicator
            if listening:
                draw_text("🎤 Listening...", font_medium, YELLOW, WIDTH//2, 420)

            # Feedback text with fade alpha
            if feedback:
                feedback_surface = font_medium.render(feedback, True, feedback_color)
                feedback_surface.set_alpha(feedback_alpha)
                feedback_rect = feedback_surface.get_rect(center=(WIDTH//2, 450))
                screen.blit(feedback_surface, feedback_rect)

            # Feedback icon with fade alpha
            if feedback_icon:
                icon_copy = feedback_icon.copy()
                icon_copy.set_alpha(feedback_alpha)
                screen.blit(icon_copy, (WIDTH//2 + 270, 430))
        else:
            draw_text("🎉 Great Job! 🎉", font_large, YELLOW, WIDTH//2, 250)
            draw_text(f"Final Score: {points}", font_medium, WHITE, WIDTH//2, 330)
            draw_text("Press 'R' to Restart", font_small, LIGHT_GRAY, WIDTH//2, 390)

        pygame.display.update()

if __name__ == "__main__":
    main()
