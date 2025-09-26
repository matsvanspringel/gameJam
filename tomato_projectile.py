# tomato.py
import pygame
import random
from projectile import Projectile

class TomatoProjectile(Projectile):
    def __init__(self, x, y, direction, speed=10, screen_width=1920, screen_height=1080):
        # Load images
        try:
            self.original_image = pygame.image.load("assets/images/tomato.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (20, 20))
            self.splat_img = pygame.image.load("assets/images/tomatosplat.png").convert_alpha()
            self.splat_img = pygame.transform.scale(self.splat_img, (30, 30))
        except Exception:
            # fallback images
            self.original_image = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 0, 0), (5, 5), 5)
            self.splat_img = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.splat_img, (200, 0, 0), (7, 7), 7)

        super().__init__(x, y, direction, speed=speed, color=(255,0,0), radius=5,
                         screen_width=screen_width, screen_height=screen_height)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.splatted = False
        self.splat_time = 0

        # Add small randomness for natural arc
        self.direction += pygame.Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.05, 0.05))
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(1, 0)
        self.direction = self.direction.normalize()

    def update(self):
        if not self.splatted:
            # use parent movement logic so pos and rect update
            super().update()
            # Zorg dat de rect altijd klopt met de positie
            self.rect.center = (self.pos.x, self.pos.y)
        else:
            # Keep splat visible for 2 seconds then remove
            if pygame.time.get_ticks() - self.splat_time >= 2000:
                self.kill()

    def hit_enemy(self):
        if not self.splatted:
            self.image = self.splat_img
            self.rect = self.image.get_rect(center=self.rect.center)
            self.splatted = True
            self.splat_time = pygame.time.get_ticks()
            # stop movement when splatted
            self.direction = pygame.Vector2(0, 0)
            self.speed = 0
