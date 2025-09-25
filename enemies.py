import random
import math
import pygame

class Enemy:
    def __init__(self, min_x, max_x, min_y, max_y, width, height, image, health, speed):
        self.x = random.randint(min_x, max_x)
        self.y = random.randint(min_y, max_y)
        self.width = width
        self.height = height
        self.image = image
        self.health = health
        self.speed = speed

    def update(self, screen_width, screen_height, player_dx, player_dy):
        # Midden van het scherm
        center_x = screen_width // 2
        center_y = screen_height // 2

        dx = center_x - self.x
        dy = center_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        # Richtingsvector naar speler
        dir_x = dx / distance
        dir_y = dy / distance

        # Projecteer spelerbeweging op richting naar enemy
        player_speed = math.hypot(player_dx, player_dy)
        if player_speed != 0:
            player_dir_x = player_dx / player_speed
            player_dir_y = player_dy / player_speed
            dot = dir_x * player_dir_x + dir_y * player_dir_y
        else:
            dot = 0

        # Pas snelheid aan: sneller als speler weg beweegt, trager als speler naar enemy beweegt
        speed_factor = 1 - 0.7 * dot  # dot: -1 (weg) tot 1 (naartoe)
        move_speed = max(0.5, self.speed * speed_factor)

        self.x += dir_x * move_speed
        self.y += dir_y * move_speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
