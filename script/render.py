import pygame

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def draw_map(screen, map_obj, offset_x=0, offset_y=0):

    tile = map_obj.tile_size
    maze = map_obj.maze

    wall_color = BLUE
    dot_color = WHITE

    for y, row in enumerate(maze):
        py = offset_y + y * tile

        for x, tile_char in enumerate(row):
            px = offset_x + x * tile

            rect = pygame.Rect(px, py, tile, tile)

            # ================= WALL =================
            if tile_char == "#":
                pygame.draw.rect(screen, wall_color, rect)

            # ================= DOT =================
            elif tile_char == ".":
                pygame.draw.circle(
                    screen,
                    dot_color,
                    rect.center,
                    max(2, tile // 8)
                )

            # ================= POWER PELLET =================
            elif tile_char == "o":
                pygame.draw.circle(
                    screen,
                    dot_color,
                    rect.center,
                    max(4, tile // 4)
                )