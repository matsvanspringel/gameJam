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

    def update(self, screen_width, screen_height, player_dx, player_dy, dt, player_x=None, player_y=None):
        # --- Animate ---
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations)
            self.image = self.animations[self.current_frame]

        # --- Movement towards the CENTER OF SCREEN ("player") ---
        target_x = screen_width // 2
        target_y = screen_height // 2

        dx = target_x - (self.x - player_x + target_x if player_x is not None else self.x)
        dy = target_y - (self.y - player_y + target_y if player_y is not None else self.y)
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        dir_x = dx / distance
        dir_y = dy / distance

        self.x += dir_x * self.speed
        self.y += dir_y * self.speed

    def draw(self, screen, player_x, player_y):
        # Draw relative to player (centered on screen)
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.width // 2
        screen_y = center_y + (self.y - player_y) - self.height // 2
        screen.blit(self.image, (screen_x, screen_y))

class SplatEffect:
    def __init__(self, x, y, duration=2000):
        # Splat should be centered at x, y (world coords)
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
        # Returns True if still alive, False if should be deleted
        return pygame.time.get_ticks() - self.start_time < self.duration

    def draw(self, screen, player_x, player_y):
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.image.get_width() // 2
        screen_y = center_y + (self.y - player_y) - self.image.get_height() // 2
        screen.blit(self.image, (screen_x, screen_y))