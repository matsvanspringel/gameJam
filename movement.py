import pygame

class Player:
    def __init__(self, speed, screen_width, screen_height):
        # Load base left-facing images
        left1 = pygame.transform.scale(
            pygame.image.load("assets/images/MainCharacter/side.png").convert_alpha(), (100, 100)
        )
        left2 = pygame.transform.scale(
            pygame.image.load("assets/images/MainCharacter/side2.png").convert_alpha(), (100, 100)
        )

        # Create right-facing by flipping left
        right1 = pygame.transform.flip(left1, True, False)
        right2 = pygame.transform.flip(left2, True, False)

        self.sprites = {
            'up': [
                pygame.transform.scale(pygame.image.load("assets/images/MainCharacter/back.png").convert_alpha(), (100, 100)),
                pygame.transform.scale(pygame.image.load("assets/images/MainCharacter/back2.png").convert_alpha(), (100, 100))
            ],
            'down': [
                pygame.transform.scale(pygame.image.load("assets/images/MainCharacter/front.png").convert_alpha(), (100, 100)),
                pygame.transform.scale(pygame.image.load("assets/images/MainCharacter/front2.png").convert_alpha(), (100, 100))
            ],
            'left': [left1, left2],
            'right': [right1, right2]
        }

        self.current_direction = 'down'
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame

        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = speed

        # Movement flags
        self.move_up = self.move_down = self.move_left = self.move_right = False

        # Use scancodes so it works for QWERTY and AZERTY
        self.up_sc = 26    # W physical key
        self.down_sc = 22  # S physical key
        self.left_sc = 4   # A physical key
        self.right_sc = 7  # D physical key

    def handle_event(self, event):
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

    def update(self, dt):
        moving = False

        dx, dy = self.get_movement_vector()
        # Diagonal speed normalization
        if dx != 0 or dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx = dx / length
            dy = dy / length
            self.x += dx * self.speed
            self.y += dy * self.speed
            moving = True

            # Update current direction
            if abs(dx) > abs(dy):
                self.current_direction = 'right' if dx > 0 else 'left'
            else:
                self.current_direction = 'down' if dy > 0 else 'up'

        # Animate if moving
        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 2
        else:
            self.frame_index = 0  # idle stays on first frame

    def draw(self, screen):
        sprite = self.sprites[self.current_direction][self.frame_index]
        screen.blit(
            sprite,
            (self.screen_width // 2 - sprite.get_width() // 2,
             self.screen_height // 2 - sprite.get_height() // 2)
        )

    def get_movement_vector(self):
        dx = dy = 0
        if self.move_up:
            dy -= 1
        if self.move_down:
            dy += 1
        if self.move_left:
            dx -= 1
        if self.move_right:
            dx += 1
        return dx, dy

    def get_direction_vector(self):
        """Returns a normalized direction vector based on movement, or up if idle."""
        dx, dy = self.get_movement_vector()
        v = pygame.Vector2(dx, dy)
        if v.length() == 0:
            return pygame.Vector2(0, -1)
        return v.normalize()