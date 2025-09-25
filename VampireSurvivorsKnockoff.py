import pygame
import sys
from background import Background
from movement import Player
from startscreen import show_start_screen
from pauzescreen import show_pause_screen
from startscreen import titlefont

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for music

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # show pause screen
            choice = show_pause_screen(screen)
            if choice == "main_menu":
                # back to startscreen
                volume = show_start_screen(screen)
                pygame.mixer.music.set_volume(volume)
            elif choice == "resume":
                pass  # go back to game
            elif choice == "quit":
                running = False  # leave game

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
