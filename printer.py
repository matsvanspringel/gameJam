import pygame

class Printer:
    def __init__(self, x, y, size=96):
        self.x = x
        self.y = y
        self.size = size
        self.image = pygame.image.load("assets/images/printer/printer2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Add a rect (for enemies)
        self.rect = pygame.Rect(self.x - self.width // 2,
                                self.y - self.height // 2,
                                self.width, self.height)

    def draw(self, screen, player_x, player_y):
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen_x = center_x + (self.x - player_x) - self.width // 2
        screen_y = center_y + (self.y - player_y) - self.height // 2
        screen.blit(self.image, (screen_x, screen_y))
