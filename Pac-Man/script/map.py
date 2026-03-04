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

        # ===== 1️⃣ BASE AVEC MURS PARTOUT =====
        for y in range(self.rows):
            row = []
            for x in range(self.cols):
                if x == 0 or x == self.cols - 1 or y == 0 or y == self.rows - 1:
                    row.append("#")
                else:
                    row.append("#")
            maze.append(row)

        # ===== 2️⃣ CREATION D'UN VRAI LABYRINTHE (DFS) =====
        visited = set()

        def carve(x, y):
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)

            visited.add((x, y))
            maze[y][x] = "."

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 1 <= nx < self.cols - 1 and 1 <= ny < self.rows - 1:
                    if (nx, ny) not in visited:
                        maze[y + dy // 2][x + dx // 2] = "."
                        carve(nx, ny)

        carve(1, 1)

        # ===== 3️⃣ SYMETRIE HORIZONTALE =====
        for y in range(self.rows):
            for x in range(self.cols // 2):
                maze[y][self.cols - 1 - x] = maze[y][x]

        # ===== 4️⃣ ZONE SPAWN CENTRALE =====
        for y in range(14, 17):
            for x in range(11, 17):
                maze[y][x] = " "

        # ===== 5️⃣ OUVERTURES LATERALES (tunnels) =====
        mid = self.rows // 2
        maze[mid][0] = "."
        maze[mid][self.cols - 1] = "."

        # ===== 6️⃣ SUPER PASTILLES =====
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