import pygame

class Background:
    def __init__(self, image_path, screen_width, screen_height, radius=4):
        self.background_img = pygame.image.load(image_path).convert()
        self.bg_width, self.bg_height = self.background_img.get_size()
        self.radius = radius
        self.tiles = {}
        self.screen_width = screen_width
        self.screen_height = screen_height

    def get_tile_coords(self, x, y):
        """Get the top-left coordinates of the tile that contains (x, y)."""
        tile_x = (x // self.bg_width) * self.bg_width
        tile_y = (y // self.bg_height) * self.bg_height
        return tile_x, tile_y

    def update_tiles(self, char_x, char_y):
        """Update which tiles should exist based on character position."""
        new_tiles = {}
        center_tile_x, center_tile_y = self.get_tile_coords(char_x, char_y)

        for row in range(-self.radius, self.radius + 1):
            for col in range(-self.radius, self.radius + 1):
                tile_pos = (
                    center_tile_x + col * self.bg_width,
                    center_tile_y + row * self.bg_height
                )
                new_tiles[tile_pos] = True
        self.tiles = new_tiles

    def draw(self, screen, char_x, char_y):
        """Draw all current tiles relative to the screen."""
        for tile_pos in self.tiles:
            screen_x = tile_pos[0] - char_x + self.screen_width // 2
            screen_y = tile_pos[1] - char_y + self.screen_height // 2
            screen.blit(self.background_img, (screen_x, screen_y))
