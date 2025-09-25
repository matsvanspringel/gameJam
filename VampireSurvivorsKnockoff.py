import pygame
import sys
from background import Background
from movement import Player
from enemies import Enemy
from startscreen import show_start_screen

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for music

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Vampire Survivors Clone")

# startscreen
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

# Create objects
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

enemy_image = pygame.image.load("Assets/Images/enemies/pizzaHigh.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
enemy = Enemy(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, 50, 50, enemy_image, health=100, speed=2)

# Load and play background music
pygame.mixer.music.load("assets/sounds/SillyMusic.mp3")
pygame.mixer.music.set_volume(0.5)  # Optional: 0.0 to 1.0
pygame.mixer.music.play(-1)  # Loop indefinitely

clock = pygame.time.Clock()
running = True
game_over = False

def check_collision(player, enemy):
    # Player is gecentreerd, enemy heeft x, y, width, height
    player_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 50,  # 100x100 sprite
        SCREEN_HEIGHT // 2 - 50,
        100, 100
    )
    enemy_rect = pygame.Rect(
        enemy.x, enemy.y, enemy.width, enemy.height
    )
    return player_rect.colliderect(enemy_rect)

while running:
    dt = clock.tick(60)  # Delta time in milliseconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if not game_over:
            player.handle_event(event)

    if not game_over:
        # Update game state
        player_dx, player_dy = player.get_movement_vector()
        player.update(dt)
        background.update_tiles(player.x, player.y)
        enemy.update(SCREEN_WIDTH, SCREEN_HEIGHT, player_dx, player_dy)

        if check_collision(player, enemy):
            game_over = True

    # Draw everything
    if game_over:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 120)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    else:
        screen.fill((0, 0, 0))
        background.draw(screen, player.x, player.y)
        enemy.draw(screen)
        player.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
