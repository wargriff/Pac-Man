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
        stack = [(1, 1)]
        maze[1][1] = DOT

        while stack:
            x, y = stack[-1]
            directions = DIRECTIONS_2[:]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if (
                    1 <= nx < self.cols - 1 and
                    1 <= ny < self.rows - 1 and
                    maze[ny][nx] == WALL
                ):
                    maze[y + dy // 2][x + dx // 2] = DOT
                    maze[ny][nx] = DOT
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()

    # ==========================================================
    # WALL SOFTENER
    # ==========================================================
    def _soften_walls(self, maze: List[List[str]]) -> None:
        intensity = 25 + self.level * 3

        for _ in range(intensity):
            x = random.randint(2, self.cols - 3)
            y = random.randint(2, self.rows - 3)

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
        maze[mid_row][0] = EMPTY
        maze[mid_row][1] = EMPTY
        maze[mid_row][self.cols - 2] = EMPTY
        maze[mid_row][self.cols - 1] = EMPTY

        # -----------------------
        # Tunnel vertical
        # -----------------------
        maze[0][mid_col] = EMPTY
        maze[1][mid_col] = EMPTY
        maze[self.rows - 2][mid_col] = EMPTY
        maze[self.rows - 1][mid_col] = EMPTY

    def wrap_position(self, x: int, y: int) -> tuple[int, int]:
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