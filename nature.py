import pygame
import random
import os

class NatureManager:
    def __init__(self, tile_size, screen_width, screen_height, scale=140, max_objects=60):
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale = scale
        self.max_objects = max_objects

        # Load and scale sprites
        self.sprites = []
        path = "assets/images/Nature"
        for i in range(1, 13):
            img = pygame.image.load(os.path.join(path, f"nature{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (scale, scale))
            self.sprites.append(img)

        bush = pygame.image.load(os.path.join(path, "bush.png")).convert_alpha()
        bush = pygame.transform.scale(bush, (scale, scale))
        self.bush = bush

        self.objects = {}  # {(tx, ty): (sprite, offset_x, offset_y)}

    def _choose_sprite(self):
        """Weighted random: bush 4x more likely"""
        choices = self.sprites + [self.bush] * 4
        return random.choice(choices)

    def update(self, player_x, player_y):
        """Spawn/despawn objects in a wide area around the player, keeping max_objects."""
        visible_area_width = self.screen_width * 2
        visible_area_height = self.screen_height * 2
        # Use integer division (//) to ensure ints for randint
        min_x = int(player_x - visible_area_width // 2)
        max_x = int(player_x + visible_area_width // 2)
        min_y = int(player_y - visible_area_height // 2)
        max_y = int(player_y + visible_area_height // 2)

        # Remove objects outside extended area
        for pos in list(self.objects.keys()):
            x, y = pos
            if x < min_x or x > max_x or y < min_y or y > max_y:
                del self.objects[pos]

        # Spawn new objects if under max_objects
        while len(self.objects) < self.max_objects:
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            sprite = self._choose_sprite()
            # Store the sprite and its position
            self.objects[(x, y)] = sprite

    def draw(self, screen, player_x, player_y):
        """Draw objects relative to player, using world coordinates."""
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        for (obj_x, obj_y), sprite in self.objects.items():
            screen_x = center_x + (obj_x - player_x) - sprite.get_width() // 2
            screen_y = center_y + (obj_y - player_y) - sprite.get_height() // 2
            screen.blit(sprite, (screen_x, screen_y))