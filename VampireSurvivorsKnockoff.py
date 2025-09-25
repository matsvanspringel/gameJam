import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Load images
background_img = pygame.image.load("assets/images/RandomAssBackground.jpg").convert()
character_img = pygame.image.load("assets/images/RandomAssVampire.png").convert_alpha()

# Character settings
char_x = SCREEN_WIDTH // 2
char_y = SCREEN_HEIGHT // 2
char_speed = 5

# Get background tile size
bg_width, bg_height = background_img.get_size()

# Movement variables
move_up = move_down = move_left = move_right = False

clock = pygame.time.Clock()

def draw_background(center_x, center_y):
    # Draw a 9x9 grid of background tiles around the character
    for row in range(-4, 5):
        for col in range(-4, 5):
            x = center_x + col * bg_width - bg_width // 2
            y = center_y + row * bg_height - bg_height // 2
            screen.blit(background_img, (x, y))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: move_up = True
            if event.key == pygame.K_DOWN: move_down = True
            if event.key == pygame.K_LEFT: move_left = True
            if event.key == pygame.K_RIGHT: move_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP: move_up = False
            if event.key == pygame.K_DOWN: move_down = False
            if event.key == pygame.K_LEFT: move_left = False
            if event.key == pygame.K_RIGHT: move_right = False

    # Update character position
    if move_up: char_y -= char_speed
    if move_down: char_y += char_speed
    if move_left: char_x -= char_speed
    if move_right: char_x += char_speed

    # Draw everything
    draw_background(SCREEN_WIDTH//2 - char_x + SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - char_y + SCREEN_HEIGHT//2)
    screen.blit(character_img, (SCREEN_WIDTH//2 - character_img.get_width()//2, SCREEN_HEIGHT//2 - character_img.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()