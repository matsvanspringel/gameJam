import pygame
import sys
from background import Background
from movement import Player
from enemies import Enemy
from startscreen import show_start_screen
from nature import NatureManager
from tomato_projectile import TomatoProjectile  # zorg dat dit bestand/klasse bestaat
from pauzescreen import show_pause_screen

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Vampire Survivors Clone")

# Load music as Sound objects for volume control
silly_music = pygame.mixer.Sound("assets/sounds/SillyMusic.mp3")
night_music = pygame.mixer.Sound("assets/sounds/nightime.mp3")  # fixed typo

# Channels for music
silly_music_channel = pygame.mixer.Channel(0)
night_music_channel = pygame.mixer.Channel(1)

silly_music_channel.play(silly_music, loops=-1)
night_music_channel.play(night_music, loops=-1)

# Separate max volumes
DAY_MAX_VOLUME = 0.5
NIGHT_MAX_VOLUME = 0.8  # Louder night music

master_volume = 1.0  # master volume die via UI wordt aangepast

silly_music_channel.set_volume(DAY_MAX_VOLUME)
night_music_channel.set_volume(0.0)  # Start muted

# Initialize day-night overlay
day_night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
day_night_overlay = day_night_overlay.convert_alpha()

# Cycle timings in milliseconds
DAY_DURATION = 30_000       # 1 minute day
NIGHT_DURATION = 30_000     # 1 minute night
TRANSITION_DURATION = 5_000  # 10 seconds transitions

cycle_timer = 0
phase = "day"  # Start with day

def update_day_night(dt):
    global cycle_timer, phase
    cycle_timer += dt
    alpha = 0

    # basis mix (0..1) zonder master
    silly_mix = 0.0
    night_mix = 0.0

    if phase == "day":
        if cycle_timer >= DAY_DURATION:
            phase = "day_to_night"
            cycle_timer = 0
        alpha = 0
        silly_mix = 1.0
        night_mix = 0.0
    elif phase == "day_to_night":
        t = min(1.0, cycle_timer / TRANSITION_DURATION)
        alpha = int(t * 140)
        silly_mix = 1.0 - t
        night_mix = t
        if cycle_timer >= TRANSITION_DURATION:
            phase = "night"
            cycle_timer = 0
    elif phase == "night":
        if cycle_timer >= NIGHT_DURATION:
            phase = "night_to_day"
            cycle_timer = 0
        alpha = 140
        silly_mix = 0.0
        night_mix = 1.0
    elif phase == "night_to_day":
        t = min(1.0, cycle_timer / TRANSITION_DURATION)
        alpha = int((1 - t) * 140)
        silly_mix = t
        night_mix = 1.0 - t
        if cycle_timer >= TRANSITION_DURATION:
            phase = "day"
            cycle_timer = 0

    day_night_overlay.fill((0, 0, 0, alpha))

    # Toepassen met master volume en per-fase max
    silly_music_channel.set_volume(master_volume * DAY_MAX_VOLUME * silly_mix)
    night_music_channel.set_volume(master_volume * NIGHT_MAX_VOLUME * night_mix)

# Startscreen
for volume in show_start_screen(screen):
    master_volume = max(0.0, min(1.0, volume))  # clamp
    # direct toepassen
    silly_music_channel.set_volume(master_volume * DAY_MAX_VOLUME)  # start in 'day'
    night_music_channel.set_volume(0.0)
    pass



# Objecten
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

enemy_image = pygame.image.load("Assets/Images/enemies/pizzaHigh.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
enemy = Enemy(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, 50, 50, enemy_image, health=100, speed=2)

nature = NatureManager(tile_size=100, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# Projectiles setup
projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300  # ms
last_shot_time = 0

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
    dt = clock.tick(60)

    # Update day-night cycle
    update_day_night(dt)

    # Update game objects
    nature.update(player.x, player.y)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        player.handle_event(event)


    # Handle shooting
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            if now - last_shot_time >= TOMATO_COOLDOWN:
                tomato = TomatoProjectile(
                    player.screen_width // 2,  # spawn at player center (screen coordinates)
                    player.screen_height // 2,
                    player.get_movement_vector(),  # add this method in Player to return facing vector
                    speed=12
                )
                projectiles.add(tomato)
                last_shot_time = now

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_over:
                    # vanuit game over terug naar main menu
                    volume = show_start_screen(screen)
                    master_volume = max(0.0, min(1.0, volume))
                    # direct toepassen (update_day_night zal elke frame ook bijsturen)
                    if phase == "day":
                        silly_music_channel.set_volume(master_volume * DAY_MAX_VOLUME)
                        night_music_channel.set_volume(0.0)
                    elif phase == "night":
                        silly_music_channel.set_volume(0.0)
                        night_music_channel.set_volume(master_volume * NIGHT_MAX_VOLUME)
                    # ... ga uit game over ...
                    game_over = False
                    game_over_time = None
                else:
                    # pauzemenu
                    choice = show_pause_screen(screen)
                    if choice == "main_menu":
                        volume = show_start_screen(screen)
                        master_volume = max(0.0, min(1.0, volume))
                        # direct toepassen
                        if phase == "day":
                            silly_music_channel.set_volume(master_volume * DAY_MAX_VOLUME)
                            night_music_channel.set_volume(0.0)
                        elif phase == "night":
                            silly_music_channel.set_volume(0.0)
                            night_music_channel.set_volume(master_volume * NIGHT_MAX_VOLUME)

                        background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
                        player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                        phase = "day"
                        enemy = Enemy(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, 50, 50, enemy_image, health=100, speed=2)
                    elif choice == "resume":
                        pass
                    elif choice == "quit":
                        running = False

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