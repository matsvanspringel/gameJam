import pygame
import sys
import random
import math
from background import Background
from movement import Player
from enemies import Enemy, SplatEffect
from startscreen import show_start_screen
from nature import NatureManager
from tomato_projectile import TomatoProjectile
from pauzescreen import show_pause_screen
from printer import Printer

pygame.init()
pygame.mixer.init()

# Screen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Vampire Survivors Clone")

# Overlays & effects
def vignette_surface(width, height, strength=1.7, alpha_max=210):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        for x in range(width):
            dx, dy = x - width // 2, y - height // 2
            dist = (dx*dx + dy*dy) ** 0.5
            max_dist = (width**2 + height**2) ** 0.5 / 2
            alpha = int(alpha_max * min(1, (dist / max_dist) ** strength))
            surf.set_at((x, y), (0, 0, 0, alpha))
    return surf

vignette_overlay = vignette_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
deep_vignette = vignette_surface(SCREEN_WIDTH, SCREEN_HEIGHT, strength=2.8, alpha_max=255)
night_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
night_tint.fill((20, 0, 50, 55))

try:
    fog_img = pygame.image.load("assets/images/fog.png").convert_alpha()
    fog_img = pygame.transform.scale(fog_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    fog_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fog_img.fill((180, 180, 200, 45))
fog_offset = 0

# Camera shake
camera_shake = 0
camera_shake_timer = 0
def trigger_camera_shake(frames=18, strength=5):
    global camera_shake, camera_shake_timer
    camera_shake = strength
    camera_shake_timer = frames

# Music
silly_music = pygame.mixer.Sound("assets/sounds/SillyMusic.mp3")
night_music = pygame.mixer.Sound("assets/sounds/nightime.mp3")
silly_music_channel = pygame.mixer.Channel(0)
night_music_channel = pygame.mixer.Channel(1)
silly_music_channel.play(silly_music, loops=-1)
night_music_channel.play(night_music, loops=-1)
DAY_MAX_VOLUME = 0.5
NIGHT_MAX_VOLUME = 0.85
silly_music_channel.set_volume(DAY_MAX_VOLUME)
night_music_channel.set_volume(0)

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

day_night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
DAY_DURATION = 10_000
NIGHT_DURATION = 25000
TRANSITION_DURATION = 5000
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
        alpha = int(t * 120)
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
        alpha = 120
    elif phase == "night_to_day":
        t = min(1.0, cycle_timer / TRANSITION_DURATION)
        alpha = int((1 - t) * 120)
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

# --- NIGHT COUNTER AND PRINTER SPAWN MAX ---
current_night_count = 0
printer_spawn_max = 3  # 3 on first night

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
        if random.random() < 0.019:
            animations = random.choice(enemy_animations)
            monsterspeed = random.uniform(2.3, 3.4) if phase == "night" else 1.3
            enemies.append(Enemy(printer, animations, health=3, speed=monsterspeed))
            trigger_camera_shake(frames=random.randint(10, 18), strength=random.randint(8, 15))

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

# --- NIGHT CREEPY STATE ---
flash_timer = 0
creep_text_timer = 0
creep_text_font = pygame.font.SysFont("Arial", 110, bold=True)
creep_texts = ["RUN", "BEHIND YOU", "STOP", "NO HOPE", "STAY STILL", "IT'S CLOSE"]

shadow_timer = 0
shadow_side = 1
shadow_y = 0

def trigger_flash():
    global flash_timer
    flash_timer = 8

def trigger_creep_text():
    global creep_text_timer
    creep_text_timer = 65

def trigger_shadow():
    global shadow_timer, shadow_side, shadow_y
    shadow_timer = 27
    shadow_side = random.choice([-1, 1])
    shadow_y = random.randint(80, SCREEN_HEIGHT-180)

def draw_creep_shadow(screen):
    surf = pygame.Surface((120, 170), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (30,30,25,210), (2, 110, 115, 48))
    pygame.draw.rect(surf, (0,0,0,230), (33, 64, 54, 75), border_radius=19)
    pygame.draw.ellipse(surf, (0,0,0,225), (23, 13, 74, 74))
    pygame.draw.ellipse(surf, (255,255,255,200), (50, 38, 12, 12))
    pygame.draw.ellipse(surf, (255,255,255,200), (73, 37, 12, 12))
    return surf

shoot_text_timer = 0
shoot_text_shake = 0
shoot_text_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 120)
shoot_text_color = (255, 32, 32)

def start_shoot_text():
    global shoot_text_timer, shoot_text_shake
    shoot_text_timer = 180
    shoot_text_shake = 13

def draw_shoot_text(surface):
    global shoot_text_timer, shoot_text_shake
    if shoot_text_timer > 0:
        txt = shoot_text_font.render("SHOOT", True, shoot_text_color)
        for _ in range(7):
            offset_x = random.randint(-shoot_text_shake, shoot_text_shake)
            offset_y = random.randint(-shoot_text_shake, shoot_text_shake)
            surface.blit(txt, (
                SCREEN_WIDTH // 2 - txt.get_width() // 2 + offset_x,
                int(SCREEN_HEIGHT * 0.22) + offset_y
            ))
        shoot_text_timer -= 1
        if shoot_text_shake > 2:
            shoot_text_shake -= 1

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

# --- DAY COUNTER/TEXT ---
day_number = 1
day_text_timer = 0
DAY_TEXT_DURATION = 180  # frames (~3 seconds at 60 FPS)
day_text_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 90)
day_text_color = (255, 255, 100)

def show_day_text():
    global day_text_timer
    day_text_timer = DAY_TEXT_DURATION

def draw_day_text(surface, day_number):
    if day_text_timer > 0:
        text = f"Day {day_number}"
        txt = day_text_font.render(text, True, day_text_color)
        x = (SCREEN_WIDTH - txt.get_width()) // 2
        y = 40
        # Optional: shadow for visibility
        shadow = day_text_font.render(text, True, (0,0,0))
        surface.blit(shadow, (x+3, y+3))
        surface.blit(txt, (x, y))

# --- Show Day 1 text immediately after start ---
show_day_text()

while running:
    dt = clock.tick(60)
    prev_phase = phase
    phase_before_update = phase
    update_day_night(dt)

    # --- Night/day transitions ---
    if phase_before_update == "night" and phase != "night":
        current_night_count += 1
        printer_spawn_max = 3 + current_night_count

    if phase_before_update != "day" and phase == "day":
        day_number = max(1, current_night_count + 1)
        show_day_text()

    # NIGHT CREEPY EVENTS
    if phase == "night" and not game_over:
        if random.random() < 0.0004:
            trigger_flash()
        if random.random() < 0.0002:
            trigger_shadow()
        if random.random() < 0.0001:
            trigger_creep_text()

    # CAMERA SHAKE update
    if camera_shake_timer > 0:
        camera_shake_timer -= 1
        dx = random.randint(-camera_shake, camera_shake)
        dy = random.randint(-camera_shake, camera_shake)
    else:
        dx = dy = 0

    printers[:] = [p for p in printers if is_printer_on_screen(p, player.x + dx, player.y + dy, SCREEN_WIDTH, SCREEN_HEIGHT)]

    if phase == "night":
        if len(printers) < printer_spawn_max and random.random() < 0.01:
            printers.append(spawn_printer_near_player(player.x + dx, player.y + dy, SCREEN_WIDTH, SCREEN_HEIGHT))
        spawn_enemies_from_printers()
    else:
        printers.clear()
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

        # SHOOT with spacebar or left mouse (after game starts)
        if ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or
            (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
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
        nature_rects = nature.get_collision_rects()
        player.update(dt, nature_collision_rects=nature_rects)
        background.update_tiles(player.x, player.y)

    projectiles.update()

    # ENEMY MOVEMENT & ANIMATION: handled inside Enemy.update
    for e in enemies:
        e.update(dt, player.x, player.y)

    # GAME OVER ON ENEMY COLLISION
    if not game_over:
        for e in enemies[:]:
            if check_collision(player, e):
                game_over = True
                trigger_flash()
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

    # DRAWING
    if day_text_timer > 0:
        day_text_timer -= 1

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
        draw_day_text(screen, day_number)

    screen.blit(day_night_overlay, (0, 0))
    if phase == "night" or game_over:
        fog_offset = (fog_offset + 1) % SCREEN_WIDTH
        screen.blit(fog_img, (-fog_offset, 0))
        if fog_offset > 0:
            screen.blit(fog_img, (SCREEN_WIDTH - fog_offset, 0))
        screen.blit(deep_vignette, (0, 0))
        screen.blit(night_tint, (0, 0))
        # Night flash (simulate lightning/fear)
        if flash_timer > 0 and flash_timer % 2 == 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255,255,255, random.randint(60,110)))
            screen.blit(flash, (0,0))
        # Shadow figure
        if shadow_timer > 0:
            shadow_img = draw_creep_shadow(screen)
            if shadow_side == 1:
                x = int(SCREEN_WIDTH * 0.85 - shadow_timer*20)
            else:
                x = int(SCREEN_WIDTH * 0.15 + shadow_timer*20)
            y = shadow_y
            alpha = max(40, min(255, shadow_timer*10))
            shadow_img.set_alpha(alpha)
            screen.blit(shadow_img, (x, y))
            shadow_timer -= 1
        # Creep text
        if creep_text_timer > 0:
            text = creep_text_font.render(random.choice(creep_texts), True, (255, 30, 30))
            for _ in range(8):
                offset_x = random.randint(-17, 17)
                offset_y = random.randint(-17, 17)
                screen.blit(text, (
                    SCREEN_WIDTH // 2 - text.get_width() // 2 + offset_x,
                    SCREEN_HEIGHT // 2 - 180 + offset_y
                ))
            creep_text_timer -= 1
        draw_shoot_text(screen)
        if flash_timer > 0:
            flash_timer -= 1

    pygame.display.flip()

pygame.quit()
sys.exit()