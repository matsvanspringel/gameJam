import math
import pygame
import random

class Enemy:
    def __init__(self, printer, animations, health, speed):
        # Spawn at printer position
        self.x = printer.x
        self.y = printer.y
        self.width = 32
        self.height = 32

        # Animation frames
        self.animations = animations  # list of surfaces
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 200  # ms per frame

        self.image = self.animations[self.current_frame]
        self.health = health
        self.speed = speed

    def update(self, dt, player_x, player_y):
        # Animate
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations)
            self.image = self.animations[self.current_frame]

        # Move toward the player's world position (always in the center of the screen)
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, screen, player_x, player_y):
        # Draw relative to player (centered on screen)
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.width // 2
        screen_y = center_y + (self.y - player_y) - self.height // 2
        screen.blit(self.image, (screen_x, screen_y))

class SplatEffect:
    # Loads the splat image only once for all instances
    _splat_img = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time = pygame.time.get_ticks()
        self.duration = 550

        # Load splat image if not loaded yet
        if SplatEffect._splat_img is None:
            try:
                img = pygame.image.load("assets/images/tomatosplat.png").convert_alpha()
                SplatEffect._splat_img = pygame.transform.scale(img, (30, 30))
            except Exception:
                # Fallback: simple red circle if image missing
                fallback = pygame.Surface((30,30), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (200, 0, 0), (15,15), 15)
                SplatEffect._splat_img = fallback

        self.splat_img = SplatEffect._splat_img

    def update(self):
        # Returns False if effect should be removed
        return pygame.time.get_ticks() - self.time < self.duration

    def draw(self, screen, player_x, player_y):
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.splat_img.get_width() // 2
        screen_y = center_y + (self.y - player_y) - self.splat_img.get_height() // 2
        screen.blit(self.splat_img, (screen_x, screen_y))