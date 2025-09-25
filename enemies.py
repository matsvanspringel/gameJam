import random

class Enemy:
    def __init__(self, min_x, max_x, min_y, max_y, height, width, image, health):
        self.x = random.randint(min_x, max_x)
        self.y = random.randint(min_y, max_y)
        self.height = height
        self.width = width
        self.image = image
        self.health = health







