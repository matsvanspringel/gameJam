import pygame
import random
from projectile import Projectile

class TomatoProjectile(Projectile):
    def __init__(self, x, y, direction, speed=10, screen_width=1920, screen_height=1080, screen_mode=False):
        # Load images
        try:
            self.original_image = pygame.image.load("assets/images/tomato.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (20, 20))
            self.splat_img = pygame.image.load("assets/images/tomatosplat.png").convert_alpha()
            self.splat_img = pygame.transform.scale(self.splat_img, (30, 30))
        except Exception:
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
        self.screen_mode = screen_mode  # True: keep in screen space only

        # No randomness if in screen mode, always straight
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(1, 0)
        self.direction = self.direction.normalize()

        # Store position as screen coordinates if in screen_mode
        if self.screen_mode:
            self.pos = pygame.Vector2(x, y)

        # Store splat world position if splatted
        self.splat_world_pos = None

    def update(self):
        if not self.splatted:
            # Move in screen coordinates if screen_mode
            if self.screen_mode:
                self.pos += self.direction * self.speed
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                # Kill if out of screen
                if (
                    self.rect.right < 0 or self.rect.left > self.screen_width
                    or self.rect.bottom < 0 or self.rect.top > self.screen_height
                ):
                    self.kill()
            else:
                super().update()
                self.rect.center = (self.pos.x, self.pos.y)
        else:
            # A splatted tomato is just a world effect, not a projectile
            if pygame.time.get_ticks() - self.splat_time >= 2000:
                self.kill()

    def hit_enemy(self):
        if not self.splatted:
            self.splatted = True
            self.splat_time = pygame.time.get_ticks()
            # Save splat world position for rendering
            self.splat_world_pos = self.get_world_pos()
            self.direction = pygame.Vector2(0, 0)
            self.speed = 0

    def get_world_pos(self):
        # Return the world coordinates where the projectile hit (for splat effect)
        if self.screen_mode:
            # Convert current screen pos to world pos by projecting from the player
            # The center of the screen is always at (player.x, player.y)
            # So offset from center is simply: (self.pos.x - center_x, self.pos.y - center_y)
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            dx = self.pos.x - center_x
            dy = self.pos.y - center_y
            # Assume player position is stored in global or passed context
            try:
                from movement import player  # Will not work, handled in draw
                world_x = player.x + dx
                world_y = player.y + dy
            except Exception:
                world_x = dx
                world_y = dy
            return (dx, dy)
        else:
            return (self.pos.x, self.pos.y)

    def draw(self, screen, player_x=None, player_y=None):
        if not self.splatted:
            # Regular projectile, draw in screen space
            screen.blit(self.image, self.rect)
        else:
            if player_x is not None and player_y is not None and self.splat_world_pos is not None:
                # Draw at fixed world position (splat), relative to player
                center_x = screen.get_width() // 2
                center_y = screen.get_height() // 2
                # World position of splat
                splat_x, splat_y = self.splat_world_pos
                screen_x = center_x + (splat_x - player_x) - self.splat_img.get_width() // 2
                screen_y = center_y + (splat_y - player_y) - self.splat_img.get_height() // 2
                screen.blit(self.splat_img, (screen_x, screen_y))
            else:
                # Fallback: draw at last screen position
                screen.blit(self.splat_img, self.rect)