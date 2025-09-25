import pygame, sys
from background import Background
from movement import Player
from startscreen import show_start_screen

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# startscreen
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

# Create objects
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player("assets/images/RandomAssVampire.png", speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        player.handle_event(event)

    # Update game state
    player.update()
    background.update_tiles(player.x, player.y)

    # Draw everything
    screen.fill((0, 0, 0))
    background.draw(screen, player.x, player.y)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
