import pygame
import sys
from background import Background
from movement import Player
from startscreen import show_start_screen
from nature import NatureManager

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for music

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

    silly_vol = 0.0
    night_vol = 0.0

    if phase == "day":
        if cycle_timer >= DAY_DURATION:
            phase = "day_to_night"
            cycle_timer = 0
        alpha = 0
        silly_vol = DAY_MAX_VOLUME
        night_vol = 0
    elif phase == "day_to_night":
        t = cycle_timer / TRANSITION_DURATION
        alpha = int(t * 140)
        silly_vol = DAY_MAX_VOLUME * (1 - t)
        night_vol = NIGHT_MAX_VOLUME * t
        if cycle_timer >= TRANSITION_DURATION:
            phase = "night"
            cycle_timer = 0
    elif phase == "night":
        if cycle_timer >= NIGHT_DURATION:
            phase = "night_to_day"
            cycle_timer = 0
        alpha = 140
        silly_vol = 0
        night_vol = NIGHT_MAX_VOLUME
    elif phase == "night_to_day":
        t = cycle_timer / TRANSITION_DURATION
        alpha = int((1 - t) * 140)
        silly_vol = DAY_MAX_VOLUME * t
        night_vol = NIGHT_MAX_VOLUME * (1 - t)
        if cycle_timer >= TRANSITION_DURATION:
            phase = "day"
            cycle_timer = 0

    day_night_overlay.fill((0, 0, 0, alpha))

    # Apply volumes
    silly_music_channel.set_volume(silly_vol)
    night_music_channel.set_volume(night_vol)

# Startscreen
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

# Create objects
background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
nature = NatureManager(tile_size=100, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

clock = pygame.time.Clock()
running = True

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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        player.handle_event(event)

    # Update player
    player.update(dt)
    background.update_tiles(player.x, player.y)

    # Draw everything
    screen.fill((0, 0, 0))
    background.draw(screen, player.x, player.y)
    nature.draw(screen, player.x, player.y)
    player.draw(screen)
    screen.blit(day_night_overlay, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
