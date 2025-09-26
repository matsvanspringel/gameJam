import pygame
import sys
import random
from background import Background
from movement import Player
from enemies import Enemy, SplatEffect  # SplatEffect will be added below
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

game_over_sound_played = False
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

silly_music = pygame.mixer.Sound("assets/sounds/SillyMusic.mp3")
night_music = pygame.mixer.Sound("assets/sounds/nightime.mp3")
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

day_night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
DAY_DURATION = 1_000
NIGHT_DURATION = 30_000
TRANSITION_DURATION = 5_000
cycle_timer = 0
phase = "day"

def update_day_night(dt):
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

printers = []
enemies = []
splat_effects = []

def is_printer_on_screen(printer, player_x, player_y, screen_w, screen_h):
    center_x = screen_w // 2
    center_y = screen_h // 2
    screen_x = center_x + (printer.x - player_x) - printer.width // 2
    screen_y = center_y + (printer.y - player_y) - printer.height // 2
    return (0 <= screen_x <= screen_w - printer.width) and (0 <= screen_y <= screen_h - printer.height)

def spawn_printer_near_player(player_x, player_y, screen_w, screen_h):
    margin = 100
    range_x = (player_x - screen_w // 2 + margin, player_x + screen_w // 2 - margin)
    range_y = (player_y - screen_h // 2 + margin, player_y + screen_h // 2 - margin)
    x = random.randint(int(range_x[0]), int(range_x[1]))
    y = random.randint(int(range_y[0]), int(range_y[1]))
    return Printer(x, y)

def spawn_enemies_from_printers():
    if not printers:
        return
    for printer in printers:
        if random.random() < 0.005:
            animations = random.choice(enemy_animations)
            enemies.append(Enemy(printer, animations, health=3, speed=1.2))

volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
nature = NatureManager(tile_size=100, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

# --- Projectiles (tomato, screen-centered only) ---
projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300
last_shot_time = 0

clock = pygame.time.Clock()
running = True
game_over = False

def check_collision(player_obj, enemy_obj):
    player_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 50,
        SCREEN_HEIGHT // 2 - 50,
        100, 100
    )
    enemy_screen_x = SCREEN_WIDTH // 2 + (enemy_obj.x - player_obj.x) - enemy_obj.width // 2
    enemy_screen_y = SCREEN_HEIGHT // 2 + (enemy_obj.y - player_obj.y) - enemy_obj.height // 2
    enemy_rect = pygame.Rect(enemy_screen_x, enemy_screen_y, enemy_obj.width, enemy_obj.height)
    return player_rect.colliderect(enemy_rect)

# --- SplatEffect class for world-space tomato splat (no hitbox!) ---
class SplatEffect:
    def __init__(self, x, y, duration=2000):
        try:
            self.image = pygame.image.load("assets/images/tomatosplat.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except Exception:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (200, 0, 0), (15, 15), 15)
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

    def draw(self, screen, player_x, player_y):
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.image.get_width() // 2
        screen_y = center_y + (self.y - player_y) - self.image.get_height() // 2
        screen.blit(self.image, (screen_x, screen_y))

while running:
    dt = clock.tick(60)
    update_day_night(dt)

    printers[:] = [p for p in printers if is_printer_on_screen(p, player.x, player.y, SCREEN_WIDTH, SCREEN_HEIGHT)]

    if phase == "night":
        if len(printers) < 3 and random.random() < 0.005:
            printers.append(spawn_printer_near_player(player.x, player.y, SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        printers.clear()
        enemies.clear()

    if phase == "night":
        spawn_enemies_from_printers()
    else:
        enemies.clear()

    nature.update(player.x, player.y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
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
        if not game_over:
            player.handle_event(event)

        # ---- SHOOTING: spawn at SCREEN CENTER, movement in screen coords only! ----
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            if now - last_shot_time >= TOMATO_COOLDOWN:
                spawn_x = SCREEN_WIDTH // 2
                spawn_y = SCREEN_HEIGHT // 2
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dir_vec = pygame.Vector2(mouse_x - spawn_x, mouse_y - spawn_y)
                if dir_vec.length_squared() == 0:
                    dir_vec = pygame.Vector2(1, 0)
                dir_vec = dir_vec.normalize()
                tomato = TomatoProjectile(
                    spawn_x, spawn_y, dir_vec, speed=12,
                    screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
                    screen_mode=True
                )
                projectiles.add(tomato)
                last_shot_time = now

    if not game_over:
        player_dx, player_dy = player.get_movement_vector()
        player.update(dt)
        background.update_tiles(player.x, player.y)

    # Update projectiles
    projectiles.update()

    # --- ENEMY MOVEMENT: Always move toward center of screen (player's rendered position) ---
    for e in list(enemies):
        screen_cx = SCREEN_WIDTH // 2
        screen_cy = SCREEN_HEIGHT // 2
        enemy_screen_x = screen_cx + (e.x - player.x) - e.width // 2
        enemy_screen_y = screen_cy + (e.y - player.y) - e.height // 2
        dx = screen_cx - enemy_screen_x
        dy = screen_cy - enemy_screen_y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        speed = e.speed
        e.x += dx / distance * speed
        e.y += dy / distance * speed

    # --- PROJECTILE/ENEMY COLLISION: Use screen hitboxes but only if projectile is active (not splatted) ---
    for e in enemies[:]:
        enemy_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + (e.x - player.x) - e.width // 2,
            SCREEN_HEIGHT // 2 + (e.y - player.y) - e.height // 2,
            e.width,
            e.height
        )
        for proj in projectiles:
            if not getattr(proj, "splatted", False) and enemy_rect.colliderect(proj.rect):
                # Spawn a splat at enemy world position
                splat_effects.append(SplatEffect(e.x, e.y))
                if hasattr(proj, "hit_enemy"):
                    proj.hit_enemy()
                enemies.remove(e)
                break

    # --- PROJECTILE/PRINTER COLLISION: Use world hitboxes, only if projectile is active (not splatted) ---
    for p in printers[:]:
        printer_hitbox = pygame.Rect(p.x - p.width // 2, p.y - p.height // 2, p.width, p.height)
        for proj in projectiles:
            if not getattr(proj, "splatted", False):
                proj_world_x = player.x + (proj.rect.centerx - SCREEN_WIDTH // 2)
                proj_world_y = player.y + (proj.rect.centery - SCREEN_HEIGHT // 2)
                if printer_hitbox.collidepoint(proj_world_x, proj_world_y):
                    splat_effects.append(SplatEffect(p.x, p.y))
                    if hasattr(proj, "hit_enemy"):
                        proj.hit_enemy()
                    printers.remove(p)
                    break

    # --- Update and remove expired splat effects ---
    splat_effects[:] = [s for s in splat_effects if s.update()]

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
    for p in printers:
        p.draw(screen, player.x, player.y)
    # Draw splat effects (below enemies)
    for splat in splat_effects:
        splat.draw(screen, player.x, player.y)
    for e in enemies:
        e.draw(screen, player.x, player.y)

    # ---- DRAW PROJECTILES at their screen position (if not splatted) ----
    for proj in projectiles:
        if not getattr(proj, "splatted", False):
            proj.draw(screen)
    player.draw(screen)
    screen.blit(day_night_overlay, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()