import pygame
from projectile import Projectile

class TomatoProjectile(Projectile):
    def __init__(self, x, y, direction, speed=10):
        # Initialize splat state
        self.splatted = False
        self.splat_time = 0

        # Load tomato image
        try:
            self.original_image = pygame.image.load("assets/images/tomato.png").convert_alpha()
            # Scale the image if needed
            self.original_image = pygame.transform.scale(self.original_image, (20, 20))
            
            # Load splat image
            self.splat_img = pygame.image.load("assets/images/tomatosplat.png").convert_alpha()
            self.splat_img = pygame.transform.scale(self.splat_img, (30, 30))
        except pygame.error:
            # Fallback to circles if images loading fails
            self.original_image = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 0, 0), (5, 5), 5)
            
            self.splat_img = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.splat_img, (200, 0, 0), (7, 7), 7)

        super().__init__(x, y, direction, speed=speed, color=(255, 0, 0), radius=5)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if not self.splatted:
            # Move only if not splatted
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

            # Kill projectile if it goes off-screen
            if (self.rect.right < 0 or self.rect.left > self.screen_width or
                self.rect.bottom < 0 or self.rect.top > self.screen_height):
                self.kill()
        else:
            # Check if 2 seconds passed since splat
            if pygame.time.get_ticks() - self.splat_time >= 2000:
                self.kill()

    def hit_enemy(self):
        """Call this when the tomato hits an enemy"""
        if not self.splatted:
            self.image = self.splat_img
            self.rect = self.image.get_rect(center=self.rect.center)  # keep position
            self.splatted = True
            self.splat_time = pygame.time.get_ticks()
