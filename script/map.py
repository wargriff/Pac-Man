import random
from typing import List, Tuple, Optional
from PIL import Image

BASE_TILE_SIZE = 20
COLS = 28
ROWS = 31

WALL = "#"
DOT = "."
POWER = "o"
EMPTY = " "

DIRECTIONS_4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


# ==========================================================
# MAP LOADER (images contenant plusieurs maps)
# ==========================================================

class MapLoader:

    def __init__(self, image_path: str, map_width: int, map_height: int):

        self.image = Image.open(image_path).convert("RGB")

        self.map_width = map_width
        self.map_height = map_height

        self.maps: List[Image.Image] = []

        self._slice_maps()

    def _slice_maps(self):

        img_w, img_h = self.image.size

        cols = img_w // self.map_width
        rows = img_h // self.map_height

        for row in range(rows):
            for col in range(cols):
                x = col * self.map_width
                y = row * self.map_height

                map_img = self.image.crop(
                    (x, y, x + self.map_width, y + self.map_height)
                )

                self.maps.append(map_img)

    def get_random_map(self) -> Image.Image:

        if not self.maps:
            raise ValueError("Aucune map trouvée dans l'image")

        return random.choice(self.maps)

    def get_map(self, index: int) -> Image.Image:

        if index < 0 or index >= len(self.maps):
            raise IndexError("Index de map invalide")

        return self.maps[index]


# ==========================================================
# MAP CLASS
# ==========================================================

class Map:

    def __init__(
            self,
            scale: float = 1.0,
            seed: Optional[int] = None,
            loader: Optional[MapLoader] = None
    ):

        # =========================
        # DIMENSIONS MAP
        # =========================
        self.cols = COLS
        self.rows = ROWS

        # =========================
        # SCALE / TILE SIZE
        # =========================
        self.scale = scale
        self.tile_size = int(BASE_TILE_SIZE * scale)

        # =========================
        # PIXEL SIZE
        # =========================
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size

        # =========================
        # LEVEL SYSTEM
        # =========================
        self.level = 1
        self.seed = seed

        # =========================
        # GAME STATS
        # =========================
        self.dots_eaten = 0

        # =========================
        # MAP STORAGE
        # =========================
        self.maze: List[List[str]] = []

        # =========================
        # MAP LOADER (optional)
        # =========================
        self.loader = loader

        # =========================
        # RANDOM SEED
        # =========================
        if self.seed is not None:
            random.seed((self.seed or 0) + self.level)

        # =========================
        # GENERATE MAP
        # =========================
        if self.loader:
            self.load_random_map_from_loader(self.loader)
        else:
            self.regenerate()

    # ==========================================================
    # UTILS
    # ==========================================================

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    # ==========================================================
    # LOAD MAP FROM IMAGE
    # ==========================================================

    def load_from_image(self, image: Image.Image):

        pixels = image.load()

        maze = []

        for y in range(self.rows):

            row = []

            for x in range(self.cols):

                px = pixels[x * self.tile_size, y * self.tile_size]
                r, g, b = px

                # Mur (noir)
                if r < 50 and g < 50 and b < 50:
                    row.append(WALL)

                # Dot (jaune)
                elif r > 200 and g > 200 and b < 100:
                    row.append(DOT)

                # Power pellet (rouge)
                elif r > 200 and g < 100 and b < 100:
                    row.append(POWER)

                # Vide
                else:
                    row.append(EMPTY)

            maze.append(row)

        self.maze = maze

    # ==========================================================
    # LOAD RANDOM MAP FROM LOADER
    # ==========================================================

    def load_random_map_from_loader(self, loader: MapLoader):

        img = loader.get_random_map()
        self.load_from_image(img)

    # ==========================================================
    # MAZE GENERATION
    # ==========================================================

    def regenerate(self):

        if self.seed is not None:
            random.seed((self.seed or 0) + self.level)

        self.maze = self._generate_maze()

    def _generate_maze(self):

        maze = [[WALL for _ in range(self.cols)] for _ in range(self.rows)]

        self._carve_paths(maze)
        self._soften_walls(maze)
        self._ensure_connectivity(maze)
        self._create_spawn_area(maze)
        self._create_tunnels(maze)
        self._place_power_pellets(maze)

        return maze

    # ==========================================================
    # CARVE PATHS
    # ==========================================================

    def _carve_paths(self, maze):

        stack = [(1, 1)]

        while stack:

            x, y = stack[-1]

            dirs = DIRECTIONS_4[:]
            random.shuffle(dirs)

            carved = False

            for dx, dy in dirs:

                nx = x + dx * 2
                ny = y + dy * 2

                if 1 <= nx < self.cols - 1 and 1 <= ny < self.rows - 1:

                    if maze[ny][nx] == WALL:

                        maze[y + dy][x + dx] = DOT
                        maze[ny][nx] = DOT

                        stack.append((nx, ny))
                        carved = True
                        break

            if not carved:
                stack.pop()

    # ==========================================================
    # SOFTEN WALLS
    # ==========================================================

    def _soften_walls(self, maze):

        for _ in range(30):

            x = random.randint(1, self.cols - 2)
            y = random.randint(1, self.rows - 2)

            if maze[y][x] == WALL:
                maze[y][x] = DOT

    # ==========================================================
    # CONNECTIVITY
    # ==========================================================

    def _ensure_connectivity(self, maze):

        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):

                if maze[y][x] != DOT:
                    continue

                walls = 0

                for dx, dy in DIRECTIONS_4:
                    if maze[y + dy][x + dx] == WALL:
                        walls += 1

                if walls >= 3:

                    dx, dy = random.choice(DIRECTIONS_4)

                    maze[y + dy][x + dx] = DOT

    # ==========================================================
    # SPAWN
    # ==========================================================

    def _create_spawn_area(self, maze):

        cx = self.cols // 2
        cy = self.rows // 2

        for y in range(cy - 1, cy + 2):
            for x in range(cx - 2, cx + 3):

                if self.in_bounds(x, y):
                    maze[y][x] = EMPTY

    # ==========================================================
    # TUNNELS
    # ==========================================================

    def _create_tunnels(self, maze):

        mid = self.rows // 2

        maze[mid][0] = EMPTY
        maze[mid][1] = EMPTY
        maze[mid][self.cols - 1] = EMPTY
        maze[mid][self.cols - 2] = EMPTY

    def _remove_dead_ends(self, maze):

        for _ in range(50):

            x = random.randint(1, self.cols - 2)
            y = random.randint(1, self.rows - 2)

            if maze[y][x] != DOT:
                continue

            walls = 0

            for dx, dy in DIRECTIONS_4:
                if maze[y + dy][x + dx] == WALL:
                    walls += 1

            if walls >= 3:
                dx, dy = random.choice(DIRECTIONS_4)
                maze[y + dy][x + dx] = DOT

    def wrap_position(self, x: int, y: int):

        if x < 0:
            x = self.cols - 1
        elif x >= self.cols:
            x = 0

        if y < 0:
            y = self.rows - 1
        elif y >= self.rows:
            y = 0

        return x, y

    # ==========================================================
    # POWER PELLETS
    # ==========================================================

    def _place_power_pellets(self, maze):

        corners = [
            (1, 1),
            (self.cols - 2, 1),
            (1, self.rows - 2),
            (self.cols - 2, self.rows - 2),
        ]

        for x, y in corners:
            maze[y][x] = POWER

    # ==========================================================
    # GAME LOGIC
    # ==========================================================

    def is_wall(self, x: int, y: int):

        if not self.in_bounds(x, y):
            return True

        return self.maze[y][x] == WALL

    def eat_dot(self, x: int, y: int):

        if not self.in_bounds(x, y):
            return None

        tile = self.maze[y][x]

        if tile == DOT:
            self.maze[y][x] = EMPTY
            self.dots_eaten += 1
            return "dot"

        if tile == POWER:
            self.maze[y][x] = EMPTY
            self.dots_eaten += 1
            return "power"

        return None

    def get_tile(self, x: int, y: int):

        if not self.in_bounds(x, y):
            return WALL

        return self.maze[y][x]

    def set_tile(self, x: int, y: int, tile):

        if self.in_bounds(x, y):
            self.maze[y][x] = tile

    def remaining_dots(self):
        for row in self.maze:
            for tile in row:
                if tile == DOT or tile == POWER:
                    return True
        return False

    # ==========================================================
    # LEVEL SYSTEM
    # ==========================================================

    def next_level(self):

        self.level += 1
        self.regenerate()

    def is_level_complete(self):

        if not self.remaining_dots():
            self.next_level()
            return True

        return False

    # ==========================================================
    # DEBUG
    # ==========================================================

    def print_maze(self):

        for row in self.maze:
            print("\n".join("".join(row) for row in self.maze))

    def get_random_empty_tile(self):

        while True:

            x = random.randint(1, self.cols - 2)
            y = random.randint(1, self.rows - 2)

            if self.maze[y][x] == EMPTY:
                return x, y

    def count_tiles(self, tile_type: str):

        return sum(row.count(tile_type) for row in self.maze)