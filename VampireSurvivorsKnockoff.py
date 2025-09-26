import pygame
import sys
import random
from background import Background
from movement import Player
from enemies import Enemy  # Animated Enemy (expects animations list, health, speed)
from startscreen import show_start_screen
from nature import NatureManager
from tomato_projectile import TomatoProjectile
from pauzescreen import show_pause_screen
from printer import Printer

# -------------------------
# Initialize Pygame & Mixer
# -------------------------
pygame.init()
pygame.mixer.init()

# -------------------------
# Screen setup (fullscreen)
# -------------------------
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Vampire Survivors Clone")

#played booleans for 1 time music
game_over_sound_played = False
# -------------------------
# Load enemy animations AFTER display is set
# -------------------------
enemy_animations = [
    [
        pygame.transform.scale(pygame.image.load("assets/images/enemies/burgerHigh.png").convert_alpha(), (50, 50)),
        pygame.transform.scale(pygame.image.load("assets/images/enemies/burgerLow.png").convert_alpha(), (50, 50)),
    ],
    [
        pygame.transform.scale(pygame.image.load("assets/images/enemies/hotdogHigh.png").convert_alpha(), (50, 50)),
        pygame.transform.scale(pygame.image.load("assets/images/enemies/hotdogLow.png").convert_alpha(), (50, 50)),
    ],
    [
        pygame.transform.scale(pygame.image.load("assets/images/enemies/pizzaHigh.png").convert_alpha(), (50, 50)),
        pygame.transform.scale(pygame.image.load("assets/images/enemies/pizzaLow.png").convert_alpha(), (50, 50)),
    ],
]

# -------------------------
# Music: load as Sound objects for crossfade control
# -------------------------
silly_music = pygame.mixer.Sound("assets/sounds/SillyMusic.mp3")
night_music = pygame.mixer.Sound("assets/sounds/nightime.mp3")  # ensure filename matches your file
game_over_sound = pygame.mixer.Sound("assets/Sounds/soundEffects/gameOver.wav")

silly_music_channel = pygame.mixer.Channel(0)
night_music_channel = pygame.mixer.Channel(1)
game_over_channel = pygame.mixer.Channel(3)

silly_music_channel.play(silly_music, loops=-1)
night_music_channel.play(night_music, loops=-1)

DAY_MAX_VOLUME = 0.5
NIGHT_MAX_VOLUME = 0.8
silly_music_channel.set_volume(DAY_MAX_VOLUME)
night_music_channel.set_volume(0.0)

# -------------------------
# Day-night overlay & timings
# -------------------------
day_night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

DAY_DURATION = 1_000        # 1 minute
NIGHT_DURATION = 30_000      # 1 minute
TRANSITION_DURATION = 5_000 # 10 seconds

cycle_timer = 0
phase = "day"  # "day", "day_to_night", "night", "night_to_day"

def update_day_night(dt):
    """Update phase, overlay alpha and music volumes (crossfade)."""
    global cycle_timer, phase
    cycle_timer += dt

    silly_vol = 0.0
    night_vol = 0.0
    alpha = 0

    if phase == "day":
        if cycle_timer >= DAY_DURATION:
            phase = "day_to_night"
            cycle_timer = 0
        silly_vol = DAY_MAX_VOLUME
        night_vol = 0.0
        alpha = 0
    elif phase == "day_to_night":
        t = min(1.0, cycle_timer / TRANSITION_DURATION)
        alpha = int(t * 140)  # darkness alpha (0..180)
        silly_vol = DAY_MAX_VOLUME * (1 - t)
        night_vol = NIGHT_MAX_VOLUME * t
        if cycle_timer >= TRANSITION_DURATION:
            phase = "night"
            cycle_timer = 0
    elif phase == "night":
        if cycle_timer >= NIGHT_DURATION:
            phase = "night_to_day"
            cycle_timer = 0
        silly_vol = 0.0
        night_vol = NIGHT_MAX_VOLUME
        alpha = 140
    elif phase == "night_to_day":
        t = min(1.0, cycle_timer / TRANSITION_DURATION)
        alpha = int((1 - t) * 140)
        silly_vol = DAY_MAX_VOLUME * t
        night_vol = NIGHT_MAX_VOLUME * (1 - t)
        if cycle_timer >= TRANSITION_DURATION:
            phase = "day"
            cycle_timer = 0

    day_night_overlay.fill((0, 0, 0, alpha))
    silly_music_channel.set_volume(silly_vol)
    night_music_channel.set_volume(night_vol)

# -------------------------
# Printers and enemies
# -------------------------
printers = []  # list of Printer objects
enemies = []   # list of Enemy objects

def is_printer_on_screen(printer, player_x, player_y, screen_w, screen_h):
    """Returns True if the printer is within the visible screen area."""
    center_x = screen_w // 2
    center_y = screen_h // 2
    screen_x = center_x + (printer.x - player_x) - printer.width // 2
    screen_y = center_y + (printer.y - player_y) - printer.height // 2
    return (0 <= screen_x <= screen_w - printer.width) and (0 <= screen_y <= screen_h - printer.height)

def spawn_printer_near_player(player_x, player_y, screen_w, screen_h):
    """Spawn a printer near the player's world position but within visible area."""
    margin = 100
    range_x = (player_x - screen_w // 2 + margin, player_x + screen_w // 2 - margin)
    range_y = (player_y - screen_h // 2 + margin, player_y + screen_h // 2 - margin)
    x = random.randint(int(range_x[0]), int(range_x[1]))
    y = random.randint(int(range_y[0]), int(range_y[1]))
    return Printer(x, y)

def spawn_enemies_from_printers():
    """For each printer, occasionally spawn an enemy (choose one of the three animations)."""
    if not printers:
        return
    for printer in printers:
        if random.random() < 0.005:  # low probability per frame
            animations = random.choice(enemy_animations)
            enemies.append(Enemy(printer, animations, health=3, speed=1.2))

# -------------------------
# Start screen & create objects
# -------------------------
volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)  # keeps compatibility with your start screen

background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

nature = NatureManager(tile_size=100, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# -------------------------
# Projectiles (tomato)
# -------------------------
projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300
last_shot_time = 0

# -------------------------
# Utility
# -------------------------
clock = pygame.time.Clock()
running = True
game_over = False

def check_collision(player_obj, enemy_obj):
    # Player is centered on screen; collide using rectangle at center
    player_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 50,
        SCREEN_HEIGHT // 2 - 50,
        100, 100
    )
    # Enemy needs to be drawn at center-relative coordinates for collision check
    enemy_screen_x = SCREEN_WIDTH // 2 + (enemy_obj.x - player_obj.x) - enemy_obj.width // 2
    enemy_screen_y = SCREEN_HEIGHT // 2 + (enemy_obj.y - player_obj.y) - enemy_obj.height // 2
    enemy_rect = pygame.Rect(enemy_screen_x, enemy_screen_y, enemy_obj.width, enemy_obj.height)
    return player_rect.colliderect(enemy_rect)

def check_projectile_enemy_collision(projectiles, enemy):
    if not enemy.visible:
        return
    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
    for proj in list(projectiles):
        # Zorg dat de rect van de projectile klopt met de huidige positie
        proj.rect.center = (proj.pos.x, proj.pos.y)
        if enemy_rect.colliderect(proj.rect):
            enemy.visible = False
            if hasattr(proj, "hit_enemy"):
                proj.hit_enemy()

while running:
    dt = clock.tick(60)  # milliseconds since last frame

    # Update day/night
    update_day_night(dt)

    # --- PRINTER MANAGEMENT: Only spawn at night with 0.005% chance every frame (and max 3 on screen) ---
    # Remove any printers that are off-screen.
    printers[:] = [p for p in printers if is_printer_on_screen(p, player.x, player.y, SCREEN_WIDTH, SCREEN_HEIGHT)]

    # Only spawn printers at night
    if phase == "night":
        # 0.005% chance per frame (0.00005 probability)
        if len(printers) < 3 and random.random() < 0.005:
            printers.append(spawn_printer_near_player(player.x, player.y, SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        # Clear printers during day
        printers.clear()
        enemies.clear()

    # Regular per-frame enemy spawn from printers (low rate), only at night
    if phase == "night":
        spawn_enemies_from_printers()
    else:
        # Clear enemies during day
        enemies.clear()

    # Update nature (works with world coords)
    nature.update(player.x, player.y)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Escape to quit
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Pause screen
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            choice = show_pause_screen(screen)
            if choice == "main_menu":
                volume = show_start_screen(screen)
                pygame.mixer.music.set_volume(volume)
                background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
                player = Player(speed=5, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                printers.clear()
                enemies.clear()
            elif choice == "resume":
                pass
            elif choice == "quit":
                running = False

        # Movement / other player events
        if not game_over:
            player.handle_event(event)


        # Handle shooting
        keys = pygame.key.get_pressed()
        # When handling shoot input, spawn at player world position:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            if now - last_shot_time >= TOMATO_COOLDOWN:
                spawn_x = player.x
                spawn_y = player.y

                # Richting naar muis in wereldcoördinaten
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = player.x + (mouse_x - SCREEN_WIDTH // 2)
                world_mouse_y = player.y + (mouse_y - SCREEN_HEIGHT // 2)
                dir_vec = pygame.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if dir_vec.length_squared() == 0:
                    dir_vec = pygame.Vector2(1, 0)
                dir_vec = dir_vec.normalize()

                tomato = TomatoProjectile(spawn_x, spawn_y, dir_vec, speed=12,
                                          screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                projectiles.add(tomato)
                last_shot_time = now
                print("spawned tomato", spawn_x, spawn_y, dir_vec)

    # Update player and background tiles
    if not game_over:
        player_dx, player_dy = player.get_movement_vector()
        player.update(dt)
        background.update_tiles(player.x, player.y)

    # Update projectiles
    projectiles.update()

    # --- ENEMY MOVEMENT: Always move toward center of screen (player's rendered position) ---
    for e in list(enemies):
        # Move toward center of screen (player is always rendered there)
        screen_cx = SCREEN_WIDTH // 2
        screen_cy = SCREEN_HEIGHT // 2
        # Calculate enemy's position on screen
        enemy_screen_x = screen_cx + (e.x - player.x) - e.width // 2
        enemy_screen_y = screen_cy + (e.y - player.y) - e.height // 2
        dx = screen_cx - enemy_screen_x
        dy = screen_cy - enemy_screen_y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        speed = e.speed
        e.x += dx / distance * speed
        e.y += dy / distance * speed

        # Update all projectiles (move them)
        for proj in list(projectiles):
            proj.update()

        # Projectile-enemy collision (continuous check)

    # --- Drawing ---
    if game_over:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 120)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    else:
        screen.fill((0, 0, 0))
        background.draw(screen, player.x, player.y)
        nature.draw(screen, player.x, player.y)  
        # Draw printers (at their rect positions)
    for p in printers:
        p.draw(screen, player.x, player.y)

    # Draw enemies
    for e in enemies:
        e.draw(screen, player.x, player.y)

    # Draw projectiles
    projectiles.draw(screen)

    # Draw player (centered)
    player.draw(screen)

    # Apply day/night overlay (after all drawing)
    screen.blit(day_night_overlay, (0, 0))

    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()
sys.exit()
