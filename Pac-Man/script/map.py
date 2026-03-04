import random

BASE_TILE_SIZE = 20
COLS = 28
ROWS = 31


class Map:

    def __init__(self, scale=1):

        self.cols = COLS
        self.rows = ROWS

        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * self.scale)

        self.update_dimensions()

        self.maze = []
        self.regenerate()

    # ==============================
    # DIMENSIONS PIXELS
    # ==============================
    def update_dimensions(self):
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size

    # ==============================
    # CHECK LIMITES
    # ==============================
    def in_bounds(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows

    # ==============================
    # GENERATION MAP
    # ==============================
    def generate_map(self):

        maze = []

        # ===== BASE STRUCTURE =====
        for y in range(self.rows):
            row = []

            for x in range(self.cols):

                # Bordures fixes
                if x == 0 or x == self.cols - 1 or y == 0 or y == self.rows - 1:
                    row.append("#")

                # Zone spawn centrale
                elif 11 <= x <= 16 and 14 <= y <= 16:
                    row.append(" ")

                else:
                    row.append(".")

            maze.append(row)

        # ===== BLOCS STRUCTURÉS =====
        for y in range(2, self.rows - 3, 2):
            for x in range(2, self.cols - 3, 2):

                if random.random() < 0.35:
                    # bloc 2x2
                    maze[y][x] = "#"
                    maze[y][x + 1] = "#"
                    maze[y + 1][x] = "#"
                    maze[y + 1][x + 1] = "#"

        # ===== COULOIRS HORIZONTAUX =====
        for y in range(4, self.rows - 4, 4):
            if random.random() < 0.5:
                for x in range(2, self.cols - 2):
                    maze[y][x] = "."

        # ===== SUPER PASTILLES =====
        maze[1][1] = "o"
        maze[1][self.cols - 2] = "o"
        maze[self.rows - 2][1] = "o"
        maze[self.rows - 2][self.cols - 2] = "o"

        return maze

    # ==============================
    def regenerate(self):
        self.maze = self.generate_map()

    # ==============================
    def set_scale(self, scale):
        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * self.scale)
        self.update_dimensions()

    # ==============================
    def is_wall(self, x, y):

        if not self.in_bounds(x, y):
            return True

        return self.maze[y][x] == "#"

    # ==============================
    def eat_dot(self, x, y):

        if not self.in_bounds(x, y):
            return None

        tile = self.maze[y][x]

        if tile == ".":
            self.maze[y][x] = " "
            return "dot"

        elif tile == "o":
            self.maze[y][x] = " "
            return "power"

        return None

    # ==============================
    def remaining_dots(self):
        return any(tile in (".", "o") for row in self.maze for tile in row)