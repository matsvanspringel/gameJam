import pygame
import random
import os

class NatureManager:
    def __init__(self, tile_size, screen_width, screen_height, scale=120, max_objects=25):
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

        # Even smaller hitbox: shrink is now 50% of scale!
        self.hitbox_shrink = int(self.scale * 0.5)

    def _choose_sprite(self):
        """Weighted random: bush 4x more likely"""
        choices = self.sprites + [self.bush] * 4
        return random.choice(choices)

    def update(self, player_x, player_y):
        """Spawn/despawn objects in a wide area around the player, keeping max_objects."""
        visible_area_width = self.screen_width * 2
        visible_area_height = self.screen_height * 2
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
        attempts = 0
        while len(self.objects) < self.max_objects and attempts < self.max_objects * 10:
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            sprite = self._choose_sprite()
            # Much smaller hitbox for nature
            shrink = self.hitbox_shrink
            nature_rect = pygame.Rect(
                x - self.scale // 2 + shrink // 2,
                y - self.scale // 2 + shrink // 2,
                self.scale - shrink,
                self.scale - shrink
            )
            # Hitbox voor speler
            player_rect = pygame.Rect(player_x - 50, player_y - 50, 100, 100)
            # Check overlap met speler
            if player_rect.colliderect(nature_rect):
                attempts += 1
                continue
            # Check overlap met bestaande natuur
            overlap = False
            for (ox, oy), _ in self.objects.items():
                other_rect = pygame.Rect(
                    ox - self.scale // 2 + shrink // 2,
                    oy - self.scale // 2 + shrink // 2,
                    self.scale - shrink,
                    self.scale - shrink
                )
                if nature_rect.colliderect(other_rect):
                    overlap = True
                    break
            if overlap:
                attempts += 1
                continue
            # Geen overlap: toevoegen
            self.objects[(x, y)] = sprite
            attempts += 1

    def draw(self, screen, player_x, player_y):
        """Draw objects relative to player, using world coordinates."""
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        for (obj_x, obj_y), sprite in self.objects.items():
            screen_x = center_x + (obj_x - player_x) - sprite.get_width() // 2
            screen_y = center_y + (obj_y - player_y) - sprite.get_height() // 2
            screen.blit(sprite, (screen_x, screen_y))

    def get_collision_rects(self):
        """
        Geeft een lijst van pygame.Rects van alle natuur-objecten, met dezelfde hitbox-marge
        als gebruikt bij het spawnen (dus met shrink).
        """
        rects = []
        shrink = self.hitbox_shrink
        for (obj_x, obj_y), sprite in self.objects.items():
            rect = pygame.Rect(
                obj_x - self.scale // 2 + shrink // 2,
                obj_y - self.scale // 2 + shrink // 2,
                self.scale - shrink,
                self.scale - shrink
            )
            rects.append(rect)
        return rects