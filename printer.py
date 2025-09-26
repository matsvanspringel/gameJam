import pygame

class Printer:
    def __init__(self, x, y, size=96):
        self.x = x
        self.y = y
        self.size = size

        # Load both images and scale
        self.image1 = pygame.image.load("assets/images/printer/printer2.png").convert_alpha()
        self.image1 = pygame.transform.scale(self.image1, (size, size))
        self.image2 = pygame.image.load("assets/images/printer/printer3.png").convert_alpha()
        self.image2 = pygame.transform.scale(self.image2, (size, size))

        self.width = self.image1.get_width()
        self.height = self.image1.get_height()

        self.spawn_time = pygame.time.get_ticks()  # Record spawn time

    def draw(self, screen, player_x, player_y):
        # Calculate fade factor (0.0 to 1.0 over 3 seconds)
        elapsed = (pygame.time.get_ticks() - self.spawn_time) / 3000
        t = max(0.0, min(elapsed, 1.0))

        # Prepare fade surfaces
        img1 = self.image1.copy()
        img2 = self.image2.copy()
        img1.set_alpha(int(255 * (1 - t)))
        img2.set_alpha(int(255 * t))

        # Draw at the correct screen position
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.width // 2
        screen_y = center_y + (self.y - player_y) - self.height // 2

        # Blit both with alpha for crossfade
        screen.blit(img1, (screen_x, screen_y))
        screen.blit(img2, (screen_x, screen_y))