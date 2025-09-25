import pygame
import sys
from background import Background
from movement import Player
from startscreen import show_start_screen
from tomato_projectile import TomatoProjectile  # zorg dat dit bestand/klasse bestaat
from pauzescreen import show_pause_screen

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Vampire Survivors Clone")

# Muziek
pygame.mixer.music.load("assets/sounds/SillyMusic.mp3")
pygame.mixer.music.play(-1)

# Startscreen en volume
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

# Objecten
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# Projectiles
projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300  # ms
last_shot_time = 0

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # beweging/animatie events naar speler
        player.handle_event(event)

        # Schieten op SPACE (KEYDOWN), met cooldown
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            if now - last_shot_time >= TOMATO_COOLDOWN:
                # Spawn bij het getekende spelercentrum (speler wordt gecentreerd op scherm)
                sprite_w = player.sprites[player.current_direction][0].get_width()
                sprite_h = player.sprites[player.current_direction][0].get_height()
                spawn_x = SCREEN_WIDTH // 2
                spawn_y = SCREEN_HEIGHT // 2

                dir_vec = player.get_direction_vector()
                # fallback als speler stilstaat (bijv. naar beneden)
                if dir_vec == (0, 0):
                    dir_vec = (0, 1)

                tomato = TomatoProjectile(spawn_x, spawn_y, dir_vec, speed=12)
                projectiles.add(tomato)
                last_shot_time = now

        # Pauze menu op ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            choice = show_pause_screen(screen)
            if choice == "main_menu":
                volume = show_start_screen(screen)
                pygame.mixer.music.set_volume(volume)
                background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
                player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                projectiles.empty()  # optioneel: wis bestaande projectielen
            elif choice == "resume":
                pass
            elif choice == "quit":
                running = False

    # Updates
    player.update(dt)
    projectiles.update()
    background.update_tiles(player.x, player.y)

    # Draw
    screen.fill((0, 0, 0))
    background.draw(screen, player.x, player.y)
    projectiles.draw(screen)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
 