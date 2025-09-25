# projectile.py
import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10, color=(255, 255, 0), radius=5, screen_width=1920, screen_height=1080):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

        # Ensure direction is a normalized Vector2
        if not isinstance(direction, pygame.Vector2):
            direction = pygame.Vector2(direction)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, -1)  # fallback
        self.direction = direction.normalize()

        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Store exact world position to handle fullscreen scrolling
        self.pos = pygame.Vector2(x, y)

    def update(self):
        # Move using world position
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        # Kill if outside the extended screen bounds (allow projectiles slightly offscreen)
        margin = 200
        if (self.rect.right < -margin or self.rect.left > self.screen_width + margin or
            self.rect.bottom < -margin or self.rect.top > self.screen_height + margin):
            self.kill()
