import pygame

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def draw_map(screen, map_obj):
    tile = map_obj.tile_size

    for y, row in enumerate(map_obj.maze):
        for x, tile_char in enumerate(row):

            rect = pygame.Rect(
                x * tile,
                y * tile,
                tile,
                tile
            )

            if tile_char == "#":
                pygame.draw.rect(screen, BLUE, rect)

            elif tile_char == ".":
                pygame.draw.circle(
                    screen,
                    WHITE,
                    rect.center,
                    tile // 8
                )