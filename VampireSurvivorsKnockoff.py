import pygame
import sys
from background import Background
from movement import Player
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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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
