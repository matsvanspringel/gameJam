import pygame
import sys
import random
from background import Background
from movement import Player
from enemies import Enemy, SplatEffect
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

# ========== NIGHT EFFECTS INITIALIZATION ==========

def create_vignette_surface(width, height):
    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        for x in range(width):
            dx = x - width // 2
            dy = y - height // 2
            dist = (dx*dx + dy*dy) ** 0.5
            max_dist = (width**2 + height**2) ** 0.5 / 2
            alpha = int(160 * min(1, (dist / max_dist) ** 1.4))
            vignette.set_at((x, y), (0, 0, 0, alpha))
    return vignette

vignette_overlay = create_vignette_surface(SCREEN_WIDTH, SCREEN_HEIGHT)

try:
    fog_img = pygame.image.load("assets/images/fog.png").convert_alpha()
    fog_img = pygame.transform.scale(fog_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    fog_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fog_img.fill((180, 180, 200, 22))
fog_offset = 0

night_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
night_tint.fill((40, 0, 80, 32))

# Camera shake
camera_shake = 0
camera_shake_timer = 0

def trigger_camera_shake(frames=16, strength=10):
    global camera_shake, camera_shake_timer
    camera_shake = strength
    camera_shake_timer = frames

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
prev_phase = "day"

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
        if random.random() < 0.01:
            animations = random.choice(enemy_animations)
            enemies.append(Enemy(printer, animations, health=3, speed=2))
            trigger_camera_shake(frames=9, strength=8)

volume = show_start_screen(screen)
pygame.mixer.music.set_volume(volume)

background = Background("assets/images/RandomAssBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(0, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
nature = NatureManager(tile_size=100, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

projectiles = pygame.sprite.Group()
TOMATO_COOLDOWN = 300
last_shot_time = 0

clock = pygame.time.Clock()
running = True
game_over = False

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

shoot_text_timer = 0
shoot_text_shake = 0
shoot_text_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 120)
shoot_text_color = (255, 32, 32)

def start_shoot_text():
    global shoot_text_timer, shoot_text_shake
    shoot_text_timer = 180  # 3 seconds at 60 FPS
    shoot_text_shake = 13

def draw_shoot_text(surface):
    global shoot_text_timer, shoot_text_shake
    if shoot_text_timer > 0:
        txt = shoot_text_font.render("SHOOT", True, shoot_text_color)
        for _ in range(8):  # Layer effect for more shake
            offset_x = random.randint(-shoot_text_shake, shoot_text_shake)
            offset_y = random.randint(-shoot_text_shake, shoot_text_shake)
            surface.blit(txt, (
                SCREEN_WIDTH // 2 - txt.get_width() // 2 + offset_x,
                int(SCREEN_HEIGHT * 0.22) + offset_y
            ))
        shoot_text_timer -= 1
        if shoot_text_shake > 2:
            shoot_text_shake -= 1  # Reduce shake over time

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

while running:
    dt = clock.tick(60)
    prev_phase = phase
    update_day_night(dt)

    # ---- CAMERA SHAKE update ----
    if camera_shake_timer > 0:
        camera_shake_timer -= 1
        dx = random.randint(-camera_shake, camera_shake)
        dy = random.randint(-camera_shake, camera_shake)
    else:
        dx = dy = 0

    printers[:] = [p for p in printers if is_printer_on_screen(p, player.x + dx, player.y + dy, SCREEN_WIDTH, SCREEN_HEIGHT)]

    if phase == "night":
        if len(printers) < 3 and random.random() < 0.005:
            printers.append(spawn_printer_near_player(player.x + dx, player.y + dy, SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        printers.clear()
        enemies.clear()

    if phase == "night":
        spawn_enemies_from_printers()
    else:
        enemies.clear()

    nature.update(player.x + dx, player.y + dy)

    if prev_phase != phase and phase == "night":
        start_shoot_text()

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
        background.update_tiles(player.x + dx, player.y + dy)

    projectiles.update()

    # --- ENEMY MOVEMENT: Always move toward center of screen (player's rendered position) ---
    for e in list(enemies):
        screen_cx = SCREEN_WIDTH // 2
        screen_cy = SCREEN_HEIGHT // 2
        enemy_screen_x = screen_cx + (e.x - player.x - dx) - e.width // 2
        enemy_screen_y = screen_cy + (e.y - player.y - dy) - e.height // 2
        ddx = screen_cx - enemy_screen_x
        ddy = screen_cy - enemy_screen_y
        distance = max(1, (ddx ** 2 + ddy ** 2) ** 0.5)
        speed = e.speed
        e.x += ddx / distance * speed
        e.y += ddy / distance * speed

    # --- GAME OVER ON ENEMY COLLISION (not printer/portal collision) ---
    if not game_over:
        for e in enemies[:]:
            if check_collision(player, e):
                game_over = True
                break

    for e in enemies[:]:
        enemy_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + (e.x - player.x - dx) - e.width // 2,
            SCREEN_HEIGHT // 2 + (e.y - player.y - dy) - e.height // 2,
            e.width,
            e.height
        )
        for proj in projectiles:
            if not getattr(proj, "splatted", False) and enemy_rect.colliderect(proj.rect):
                splat_effects.append(SplatEffect(e.x, e.y))
                if hasattr(proj, "hit_enemy"):
                    proj.hit_enemy()
                enemies.remove(e)
                trigger_camera_shake(frames=8, strength=6)
                break

    for p in printers[:]:
        printer_hitbox = pygame.Rect(p.x - p.width // 2, p.y - p.height // 2, p.width, p.height)
        for proj in projectiles:
            if not getattr(proj, "splatted", False):
                proj_world_x = player.x + dx + (proj.rect.centerx - SCREEN_WIDTH // 2)
                proj_world_y = player.y + dy + (proj.rect.centery - SCREEN_HEIGHT // 2)
                if printer_hitbox.collidepoint(proj_world_x, proj_world_y):
                    splat_effects.append(SplatEffect(p.x, p.y))
                    if hasattr(proj, "hit_enemy"):
                        proj.hit_enemy()
                    printers.remove(p)
                    trigger_camera_shake(frames=8, strength=5)
                    break

    splat_effects[:] = [s for s in splat_effects if s.update()]

    # ---------- DRAWING ----------
    if game_over:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 120)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    else:
        screen.fill((0, 0, 0))
        background.draw(screen, player.x + dx, player.y + dy)
        nature.draw(screen, player.x + dx, player.y + dy)
        for p in printers:
            p.draw(screen, player.x + dx, player.y + dy)
        for splat in splat_effects:
            splat.draw(screen, player.x + dx, player.y + dy)
        for e in enemies:
            e.draw(screen, player.x + dx, player.y + dy)
        for proj in projectiles:
            if not getattr(proj, "splatted", False):
                proj.draw(screen)
        player.draw(screen)

    screen.blit(day_night_overlay, (0, 0))
    if phase == "night":
        fog_offset = (fog_offset + 1) % SCREEN_WIDTH
        screen.blit(fog_img, (-fog_offset, 0))
        if fog_offset > 0:
            screen.blit(fog_img, (SCREEN_WIDTH - fog_offset, 0))
        screen.blit(vignette_overlay, (0, 0))
        screen.blit(night_tint, (0, 0))
        draw_shoot_text(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()