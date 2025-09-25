import pygame

class Player:
    def __init__(self, image_path, speed, screen_width, screen_height):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.x = 0
        self.y = 0
        self.speed = speed
        self.move_up = self.move_down = self.move_left = self.move_right = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Scancodes for WASD physical key positions
        self.up_sc = 26     # W key position
        self.down_sc = 22   # S key position
        self.left_sc = 4    # A key position
        self.right_sc = 7   # D key position

    def handle_event(self, event):
        """Handle movement input events."""
        if event.type == pygame.KEYDOWN:
            sc = event.scancode
            if sc == self.up_sc: self.move_up = True
            if sc == self.down_sc: self.move_down = True
            if sc == self.left_sc: self.move_left = True
            if sc == self.right_sc: self.move_right = True
        elif event.type == pygame.KEYUP:
            sc = event.scancode
            if sc == self.up_sc: self.move_up = False
            if sc == self.down_sc: self.move_down = False
            if sc == self.left_sc: self.move_left = False
            if sc == self.right_sc: self.move_right = False

    def update(self):
        """Update player position based on movement flags."""
        if self.move_up: self.y -= self.speed
        if self.move_down: self.y += self.speed
        if self.move_left: self.x -= self.speed
        if self.move_right: self.x += self.speed

    def draw(self, screen):
        """Draw player at the center of the screen."""
        screen.blit(
            self.image,
            (self.screen_width // 2 - self.image.get_width() // 2,
             self.screen_height // 2 - self.image.get_height() // 2)
        )
