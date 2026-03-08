import random
import pygame


class Fruit:

    FRUIT_TYPES = {
        1: ("cherry", 100, (255, 0, 0)),
        2: ("strawberry", 300, (255, 100, 100)),
        3: ("orange", 500, (255, 165, 0)),
        4: ("apple", 700, (255, 0, 100)),
        5: ("melon", 1000, (0, 255, 0)),
        6: ("galaxian", 2000, (0, 255, 255)),
        7: ("bell", 3000, (255, 255, 0)),
        8: ("key", 5000, (255, 255, 255)),
    }

    def __init__(self, level, map_obj):
        self.level = min(level, 8)
        self.name, self.score_value, self.color = self.FRUIT_TYPES[self.level]

        self.x = map_obj.cols // 2
        self.y = map_obj.rows // 2 + 3

        self.visible = False
        self.timer = 0

    def spawn(self):
        self.visible = True
        self.timer = 600  # 10 sec à 60fps

    def update(self):
        if self.visible:
            self.timer -= 1
            if self.timer <= 0:
                self.visible = False

    def draw(self, screen, offset_x, offset_y, tile_size):
        if not self.visible:
            return

        px = offset_x + self.x * tile_size
        py = offset_y + self.y * tile_size

        pygame.draw.circle(
            screen,
            self.color,
            (px + tile_size // 2, py + tile_size // 2),
            tile_size // 3
        )