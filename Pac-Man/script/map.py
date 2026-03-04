import random
from typing import List

BASE_TILE_SIZE = 20
COLS = 28
ROWS = 31

WALL = "#"
DOT = "."
POWER = "o"
EMPTY = " "


class Map:
    def __init__(self, scale: float = 1.0):
        self.cols = COLS
        self.rows = ROWS

        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * self.scale)

        self.level = 1
        self.maze: List[List[str]] = []

        self.update_dimensions()
        self.regenerate()

    # ==========================================================
    # DIMENSIONS
    # ==========================================================
    def update_dimensions(self) -> None:
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size

    def set_scale(self, scale: float) -> None:
        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * self.scale)
        self.update_dimensions()

    # ==========================================================
    # BOUNDS
    # ==========================================================
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    # ==========================================================
    # MAP GENERATION
    # ==========================================================
    def regenerate(self) -> None:
        self.maze = self._generate_maze()

    def _ensure_connectivity(self, maze):
        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):

                if maze[y][x] == DOT:
                    walls = 0
                    neighbors = []

                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if maze[y + dy][x + dx] == WALL:
                            walls += 1
                            neighbors.append((x + dx, y + dy))

                    # Si trop fermé → ouvrir un mur
                    if walls >= 3 and neighbors:
                        nx, ny = random.choice(neighbors)
                        maze[ny][nx] = DOT

    def _generate_maze(self):

        # Base pleine de murs
        maze = [[WALL for _ in range(self.cols)] for _ in range(self.rows)]

        # ===============================
        # 1️⃣ Génération labyrinthe doux
        # ===============================
        visited = set()

        def carve(x, y):
            visited.add((x, y))
            maze[y][x] = DOT

            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 1 <= nx < self.cols - 1 and 1 <= ny < self.rows - 1:
                    if (nx, ny) not in visited:
                        maze[y + dy // 2][x + dx // 2] = DOT
                        carve(nx, ny)

        carve(1, 1)

        # ===============================
        # 2️⃣ Ouvrir des zones pour respirer
        # ===============================
        for _ in range(40):  # plus le nombre est grand → plus c'est ouvert
            x = random.randint(2, self.cols - 3)
            y = random.randint(2, self.rows - 3)

            if maze[y][x] == WALL:
                maze[y][x] = DOT

        # ===============================
        # 3️⃣ Nettoyage anti cul-de-sac
        # ===============================
        self._ensure_connectivity(maze)

        # ===============================
        # 4️⃣ Spawn + tunnels + power
        # ===============================
        self._create_spawn_area(maze)
        self._create_tunnels(maze)
        self._place_power_pellets(maze)

        return maze

    # ==========================================================
    # MAP MODIFIERS
    # ==========================================================
    def _apply_horizontal_symmetry(self, maze: List[List[str]]) -> None:
        for y in range(self.rows):
            for x in range(self.cols // 2):
                maze[y][self.cols - 1 - x] = maze[y][x]

    def _create_spawn_area(self, maze: List[List[str]]) -> None:
        center_y = self.rows // 2
        center_x = self.cols // 2

        # ==========================
        # Zone maison fantômes vide
        # ==========================
        for y in range(center_y - 1, center_y + 2):
            for x in range(center_x - 3, center_x + 3):
                if self.in_bounds(x, y):
                    maze[y][x] = EMPTY

        # ==========================
        # Ouvrir accès gauche / droite
        # ==========================
        if self.in_bounds(center_x - 4, center_y):
            maze[center_y][center_x - 4] = DOT

        if self.in_bounds(center_x + 3, center_y):
            maze[center_y][center_x + 3] = DOT

        # ==========================
        # Ouvrir accès haut / bas
        # ==========================
        if self.in_bounds(center_x, center_y - 2):
            maze[center_y - 2][center_x] = DOT

        if self.in_bounds(center_x, center_y + 2):
            maze[center_y + 2][center_x] = DOT

    def _create_tunnels(self, maze: List[List[str]]) -> None:

        # Tunnel horizontal (gauche / droite)
        mid_row = self.rows // 2
        maze[mid_row][0] = EMPTY
        maze[mid_row][self.cols - 1] = EMPTY

        # Tunnel vertical (haut / bas)
        mid_col = self.cols // 2
        maze[0][mid_col] = EMPTY
        maze[self.rows - 1][mid_col] = EMPTY

    def _place_power_pellets(self, maze: List[List[str]]) -> None:
        positions = [
            (1, 1),
            (self.cols - 2, 1),
            (1, self.rows - 2),
            (self.cols - 2, self.rows - 2),
        ]

        for x, y in positions:
            maze[y][x] = POWER

    # ==========================================================
    # GAME LOGIC
    # ==========================================================
    def is_wall(self, x: int, y: int) -> bool:

        # Tunnel horizontal
        if y == self.rows // 2:
            if x < 0 or x >= self.cols:
                return False

        # Tunnel vertical
        if x == self.cols // 2:
            if y < 0 or y >= self.rows:
                return False

        if not self.in_bounds(x, y):
            return True

        return self.maze[y][x] == WALL

    def eat_dot(self, x: int, y: int):
        if not self.in_bounds(x, y):
            return None

        tile = self.maze[y][x]

        if tile == DOT:
            self.maze[y][x] = EMPTY
            return "dot"

        if tile == POWER:
            self.maze[y][x] = EMPTY
            return "power"

        return None

    def remaining_dots(self) -> bool:
        return any(tile in (DOT, POWER) for row in self.maze for tile in row)

    # ==========================================================
    # LEVEL SYSTEM
    # ==========================================================
    def next_level(self) -> None:
        self.level += 1
        self.regenerate()

    def is_level_complete(self) -> bool:
        if not self.remaining_dots():
            self.next_level()
            return True
        return False