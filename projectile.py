# projectile.py
import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10, color=(255,255,0), radius=5, screen_width=800, screen_height=600):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        if not isinstance(direction, pygame.Vector2):
            direction = pygame.Vector2(direction)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(0, -1)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        if (self.rect.right < 0 or self.rect.left > self.screen_width or
            self.rect.bottom < 0 or self.rect.top > self.screen_height):
            self.kill()
