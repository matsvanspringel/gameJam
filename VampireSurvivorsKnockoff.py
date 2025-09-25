import pygame
import sys
from background import Background
from movement import Player  # Your updated Player class with animations

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for music

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Create objects
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# Load and play background music
pygame.mixer.music.load("assets/sounds/SillyMusic.mp3")
pygame.mixer.music.set_volume(0.5)  # Optional: 0.0 to 1.0
pygame.mixer.music.play(-1)  # Loop indefinitely

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)  # Delta time in milliseconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        player.handle_event(event)

    # Update game state
    player.update(dt)
    background.update_tiles(player.x, player.y)

    # Draw everything
    screen.fill((0, 0, 0))
    background.draw(screen, player.x, player.y)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
