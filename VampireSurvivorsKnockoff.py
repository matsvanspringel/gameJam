import pygame
import sys
from background import Background
from movement import Player
from startscreen import show_start_screen
from tomato_projectile import TomatoProjectile  # make sure this is correct

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Startscreen
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

# Create objects
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# Load and play background music
pygame.mixer.music.load("assets/sounds/SillyMusic.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Projectiles setup
projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300  # milliseconds
last_shot_time = 0

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        player.handle_event(event)

    # Handle shooting
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        now = pygame.time.get_ticks()
        if now - last_shot_time >= TOMATO_COOLDOWN:
            tomato = TomatoProjectile(
                player.screen_width // 2,  # spawn at player center (screen coordinates)
                player.screen_height // 2,
                player.get_direction_vector(),  # add this method in Player to return facing vector
                speed=12
            )
            projectiles.add(tomato)
            last_shot_time = now

    # Update game state
    player.update(dt)
    projectiles.update()
    background.update_tiles(player.x, player.y)

    # Draw everything
    screen.fill((0, 0, 0))
    background.draw(screen, player.x, player.y)
    projectiles.draw(screen)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
 