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
        self.visible = True  # Add visible attribute

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

        # If player_x and player_y are provided, use them as world coordinates;
        # but for your requirement, always use screen center as the destination.
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
        if self.visible:
            screen.blit(self.image, (screen_x, screen_y))