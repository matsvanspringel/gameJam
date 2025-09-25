import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Load and scale images
background_img = pygame.image.load("assets/images/RandomAssBackground.jpg").convert()
character_img = pygame.image.load("assets/images/RandomAssVampire.png").convert_alpha()
character_img = pygame.transform.scale(character_img, (100, 100))  # Scale character down

# Character settings
char_x = 0
char_y = 0
char_speed = 5

# Tile settings
bg_width, bg_height = background_img.get_size()
radius = 4  # 9x9 radius = 4 tiles in each direction

# Track tiles that are currently drawn
tiles = {}

# Movement variables
move_up = move_down = move_left = move_right = False

clock = pygame.time.Clock()

def get_tile_coords(x, y):
    """Get the top-left coordinates of the tile that contains (x, y)"""
    tile_x = (x // bg_width) * bg_width
    tile_y = (y // bg_height) * bg_height
    return tile_x, tile_y

def update_tiles():
    """Update which tiles should exist based on character position"""
    global tiles
    new_tiles = {}
    # Character is at (char_x, char_y)
    center_tile_x, center_tile_y = get_tile_coords(char_x, char_y)
    # Spawn tiles in a 9x9 grid around the character
    for row in range(-radius, radius + 1):
        for col in range(-radius, radius + 1):
            tile_pos = (center_tile_x + col * bg_width, center_tile_y + row * bg_height)
            new_tiles[tile_pos] = True
    tiles = new_tiles

def draw_tiles():
    """Draw all current tiles relative to the screen"""
    for tile_pos in tiles:
        screen_x = tile_pos[0] - char_x + SCREEN_WIDTH // 2
        screen_y = tile_pos[1] - char_y + SCREEN_HEIGHT // 2
        screen.blit(background_img, (screen_x, screen_y))

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

    # Update tiles
    update_tiles()

    # Draw everything
    screen.fill((0, 0, 0))
    draw_tiles()
    # Draw character at the center
    screen.blit(character_img, (SCREEN_WIDTH//2 - character_img.get_width()//2,
                                SCREEN_HEIGHT//2 - character_img.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()