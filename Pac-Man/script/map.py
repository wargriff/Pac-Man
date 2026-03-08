import random
from typing import List, Tuple, Optional

BASE_TILE_SIZE = 20
COLS = 28
ROWS = 31

WALL = "#"
DOT = "."
POWER = "o"
EMPTY = " "

DIRECTIONS_4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRECTIONS_2 = [(2, 0), (-2, 0), (0, 2), (0, -2)]


class Map:
    """
    Advanced procedural maze generator for Pac-Man style gameplay.
    """

    # ==========================================================
    # INIT
    # ==========================================================
    def __init__(self, scale: float = 1.0, seed: Optional[int] = None):
        self.cols = COLS
        self.rows = ROWS

        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * self.scale)

        self.level = 1
        self.seed = seed

        self.width = 0
        self.height = 0
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
    # UTILS
    # ==========================================================
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_edge(self, x: int, y: int) -> bool:
        return x == 0 or y == 0 or x == self.cols - 1 or y == self.rows - 1

    # ==========================================================
    # REGENERATION
    # ==========================================================
    def regenerate(self) -> None:
        if self.seed is not None:
            random.seed(self.seed + self.level)

        self.maze = self._generate_maze()

    # ==========================================================
    # MAZE GENERATION CORE
    # ==========================================================
    def _generate_maze(self) -> List[List[str]]:

        maze = [[WALL for _ in range(self.cols)] for _ in range(self.rows)]

        self._carve_paths_iterative(maze)
        self._soften_walls(maze)
        self._ensure_connectivity(maze)
        self._apply_difficulty(maze)
        self._create_spawn_area(maze)
        self._create_tunnels(maze)
        self._place_power_pellets(maze)

        return maze

    # ==========================================================
    # DFS ITERATIVE CARVING
    # ==========================================================
    def _carve_paths_iterative(self, maze: List[List[str]]) -> None:

        # Logical grid groups cells in 4x4 blocks; ensure at least 1x1
        logical_cols = max(1, self.cols // 4)
        logical_rows = max(1, self.rows // 4)

        grid = [[WALL for _ in range(logical_cols)] for _ in range(logical_rows)]

        stack = [(0, 0)]
        grid[0][0] = DOT

        directions = DIRECTIONS_4[:]

        while stack:
            x, y = stack[-1]
            dirs = directions[:]
            random.shuffle(dirs)

            carved = False

            for dx, dy in dirs:
                nx = x + dx
                ny = y + dy

                if 0 <= nx < logical_cols and 0 <= ny < logical_rows and grid[ny][nx] == WALL:
                    grid[ny][nx] = DOT
                    stack.append((nx, ny))
                    carved = True
                    break

            if not carved:
                stack.pop()

        # Expand logical grid into the real maze (3x3 open blocks inside each 4x4 cell)
        for gy in range(logical_rows):
            for gx in range(logical_cols):

                if grid[gy][gx] == DOT:

                    base_x = gx * 4 + 1
                    base_y = gy * 4 + 1

                    for dy in range(3):
                        for dx in range(3):
                            tx = base_x + dx
                            ty = base_y + dy
                            if self.in_bounds(tx, ty):
                                maze[ty][tx] = DOT

    # ==========================================================
    # WALL SOFTENER
    # ==========================================================
    def _soften_walls(self, maze: List[List[str]]) -> None:
        intensity = 25 + self.level * 3

        # avoid selecting border cells to prevent accidental out-of-bounds
        min_x = 2
        max_x = max(2, self.cols - 3)
        min_y = 2
        max_y = max(2, self.rows - 3)

        for _ in range(intensity):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            if maze[y][x] == WALL:
                maze[y][x] = DOT

    # ==========================================================
    # CONNECTIVITY CLEANER
    # ==========================================================
    def _ensure_connectivity(self, maze: List[List[str]]) -> None:
        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):

                if maze[y][x] != DOT:
                    continue

                walls = [
                    (x + dx, y + dy)
                    for dx, dy in DIRECTIONS_4
                    if maze[y + dy][x + dx] == WALL
                ]

                open_paths = 4 - len(walls)

                if open_paths <= 1 and walls:
                    nx, ny = random.choice(walls)
                    maze[ny][nx] = DOT

    # ==========================================================
    # DIFFICULTY SYSTEM
    # ==========================================================
    def _apply_difficulty(self, maze: List[List[str]]) -> None:
        """
        Higher levels = slightly tighter maze.
        """
        if self.level < 3:
            return

        reduction = min(self.level * 2, 40)

        for _ in range(reduction):
            x = random.randint(2, self.cols - 3)
            y = random.randint(2, self.rows - 3)

            if maze[y][x] == DOT:
                maze[y][x] = WALL

    # ==========================================================
    # SPAWN ZONE
    # ==========================================================
    def _create_spawn_area(self, maze: List[List[str]]) -> None:
        cx = self.cols // 2
        cy = self.rows // 2

        for y in range(cy - 1, cy + 2):
            for x in range(cx - 3, cx + 3):
                if self.in_bounds(x, y):
                    maze[y][x] = EMPTY

    # ==========================================================
    # TUNNELS
    # ==========================================================
    def _create_tunnels(self, maze: List[List[str]]) -> None:
        mid_row = self.rows // 2
        mid_col = self.cols // 2

        # -----------------------
        # Tunnel horizontal
        # -----------------------
        if self.in_bounds(0, mid_row):
            maze[mid_row][0] = EMPTY
        if self.in_bounds(1, mid_row):
            maze[mid_row][1] = EMPTY
        if self.in_bounds(self.cols - 2, mid_row):
            maze[mid_row][self.cols - 2] = EMPTY
        if self.in_bounds(self.cols - 1, mid_row):
            maze[mid_row][self.cols - 1] = EMPTY

        # -----------------------
        # Tunnel vertical
        # -----------------------
        if self.in_bounds(mid_col, 0):
            maze[0][mid_col] = EMPTY
        if self.in_bounds(mid_col, 1):
            maze[1][mid_col] = EMPTY
        if self.in_bounds(mid_col, self.rows - 2):
            maze[self.rows - 2][mid_col] = EMPTY
        if self.in_bounds(mid_col, self.rows - 1):
            maze[self.rows - 1][mid_col] = EMPTY

    def wrap_position(self, x: int, y: int) -> Tuple[int, int]:
        """
        Gère la téléportation sur les bords.
        """
        mid_row = self.rows // 2
        mid_col = self.cols // 2

        # Tunnel horizontal
        if y == mid_row:
            if x < 0:
                return self.cols - 1, y
            if x >= self.cols:
                return 0, y

        # Tunnel vertical
        if x == mid_col:
            if y < 0:
                return x, self.rows - 1
            if y >= self.rows:
                return x, 0

        return x, y

    # ==========================================================
    # POWER PELLETS
    # ==========================================================
    def _place_power_pellets(self, maze: List[List[str]]) -> None:
        positions = [
            (1, 1),
            (self.cols - 2, 1),
            (1, self.rows - 2),
            (self.cols - 2, self.rows - 2),
        ]

        for x, y in positions:
            if not self.in_bounds(x, y):
                continue
            # don't overwrite EMPTY (spawn/tunnel) — prefer placing on DOT or WALL
            if maze[y][x] != EMPTY:
                maze[y][x] = POWER

    # ==========================================================
    # GAME LOGIC
    # ==========================================================
    def is_wall(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        return self.maze[y][x] == WALL

    def eat_dot(self, x: int, y: int) -> Optional[str]:
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
        return any(
            tile in (DOT, POWER)
            for row in self.maze
            for tile in row
        )

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

    # ==========================================================
    # DEBUG TOOLS
    # ==========================================================
    def print_maze(self) -> None:
        for row in self.maze:
            print("".join(row))

    def count_tiles(self, tile_type: str) -> int:
        return sum(row.count(tile_type) for row in self.maze)