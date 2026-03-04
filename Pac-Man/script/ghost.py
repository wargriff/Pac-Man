import random
import os
from script.animation import Animation
from script.ai import GhostAI


class Ghost:

    DIRECTIONS = {
        "right": (1, 0),
        "left": (-1, 0),
        "down": (0, 1),
        "up": (0, -1)
    }

    def __init__(self, x, y, folder_path, tile_size, speed):

        # ----------------------------------
        # POSITION
        # ----------------------------------
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y

        # ----------------------------------
        # CONFIG
        # ----------------------------------
        self.tile_size = tile_size
        self.base_speed = speed  # vitesse normale
        self.base_speed = speed
        self.speed = speed + 4  # Plus lent au début
        self.timer = 0
        self.spawn_delay = 120  # 2 secondes tranquille

        # Nom du dossier (blinky, boss_01, etc.)
        self.name = os.path.basename(folder_path).lower()

        # ----------------------------------
        # ANIMATIONS
        # ----------------------------------
        self.animations = self.load_animations(folder_path)
        self.current_direction = "left"

        # ----------------------------------
        # TYPE (ghost normal ou boss)
        # ----------------------------------
        self.is_boss = "boss" in self.name

        # ----------------------------------
        # SYSTEME DE VIE
        # ----------------------------------
        if self.is_boss:
            self.max_hp = 10
            self.hp = self.max_hp
        else:
            self.max_hp = 1
            self.hp = 1

        # ----------------------------------
        # PHASE SYSTEM (boss uniquement)
        # ----------------------------------
        self.phase = 1  # Phase 1 par défaut

        # ----------------------------------
        # TELEPORT COOLDOWN (boss_02)
        # ----------------------------------
        self.teleport_cooldown = 0
        self.max_teleport_cooldown = 120  # frames

        # ----------------------------------
        # IA
        # ----------------------------------
        self.ai = GhostAI(self)

    # --------------------------------------------------
    # LOAD ANIMATIONS
    # --------------------------------------------------
    def load_animations(self, base_path):
        animations = {}

        print("Loading ghost from:", base_path)  # 👈 debug

        for direction in self.DIRECTIONS:
            path = os.path.join(base_path, direction)
            print("Checking:", path)  # 👈 debug

            if os.path.exists(path):
                animations[direction] = Animation(
                    path,
                    self.tile_size,
                    speed=10
                )

        print("Loaded directions:", animations.keys())  # 👈 debug

        return animations

    # --------------------------------------------------
    # BOSS 01 - AGRESSIF
    # --------------------------------------------------
    def boss1_behavior(self, maze, player_x, player_y):

        # Phase 1 : chasse normale
        if self.phase == 1:
            return self.move_towards(maze, player_x, player_y)

        # Phase 2 : prédiction du joueur
        future_x = player_x + random.choice([-1, 1])
        future_y = player_y + random.choice([-1, 1])

        return self.move_towards(maze, future_x, future_y)

    # --------------------------------------------------
    # BOSS 02 - TELEPORT
    # --------------------------------------------------
    def boss2_behavior(self, maze, player_x, player_y):

        # 20% chance de téléportation
        if random.random() < 0.2:
            self.teleport(maze)
            return (0, 0)

        if self.phase == 2:
            # Phase 2 → fuite puis attaque
            if random.random() < 0.5:
                return self.move_away(maze, player_x, player_y)

        return self.move_towards(maze, player_x, player_y)

    def teleport(self, maze):

        valid_positions = []

        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] != "#":
                    valid_positions.append((x, y))

        if valid_positions:
            self.x, self.y = random.choice(valid_positions)

    def take_damage(self, amount=1):
        if "boss" in self.name:
            self.hp -= amount
            if self.hp <= 0:
                self.reset()
                self.hp = self.max_hp
                self.phase = 1

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update(self, map_obj, player_x, player_y):

        # =============================
        # TIMER MOUVEMENT
        # =============================
        self.timer += 1

        if self.timer >= self.speed:
            self.timer = 0

            if self.spawn_delay > 0:
                self.spawn_delay -= 1
                return

            # ✅ correction ici
            maze = map_obj.maze

            dx, dy = self.choose_direction(maze, player_x, player_y)

            new_x = self.x + dx
            new_y = self.y + dy

            if self.is_valid_move(maze, new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.update_direction(dx, dy)

        # =============================
        # TUNNEL
        # =============================
        self.handle_tunnel(map_obj)

        # =============================
        # ANIMATION
        # =============================
        self.animations[self.current_direction].update()

        # Ajustement difficulté selon score
        if hasattr(map_obj, "score"):
            if map_obj.score > 1500:
                self.speed = self.base_speed
            elif map_obj.score > 500:
                self.speed = self.base_speed + 2
            else:
                self.speed = self.base_speed + 4

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    def is_valid_move(self, maze, x, y):
        if 0 <= y < len(maze) and 0 <= x < len(maze[0]):
            return maze[y][x] != "#"
        return False

    # --------------------------------------------------
    # DIRECTION UPDATE
    # --------------------------------------------------
    def update_direction(self, dx, dy):
        for name, (dir_x, dir_y) in self.DIRECTIONS.items():
            if (dx, dy) == (dir_x, dir_y):
                self.current_direction = name
                break

    # --------------------------------------------------
    # IA PRINCIPALE
    # --------------------------------------------------
    def choose_direction(self, maze, player_x, player_y):

        distance = abs(self.x - player_x) + abs(self.y - player_y)

        behaviors = {
            "blinky": lambda: self.move_towards(maze, player_x, player_y),
            "pinky": lambda: self.move_towards(maze, player_x + 2, player_y),
            "inky": lambda: self.move_towards(maze, player_x, player_y)
                              if random.random() < 0.6
                              else self.random_move(maze),
            "clyde": lambda: self.move_away(maze, player_x, player_y)
                              if distance < 5
                              else self.move_towards(maze, player_x, player_y)
        }

        return behaviors.get(self.name, lambda: self.random_move(maze))()

    # --------------------------------------------------
    # MOVE TOWARDS / AWAY
    # --------------------------------------------------
    def move_towards(self, maze, target_x, target_y):
        return self.best_move(maze, target_x, target_y, reverse=False)

    def move_away(self, maze, target_x, target_y):
        return self.best_move(maze, target_x, target_y, reverse=True)

    def best_move(self, maze, target_x, target_y, reverse=False):

        best_move = (0, 0)
        best_distance = -1 if reverse else float("inf")

        for dx, dy in self.DIRECTIONS.values():

            nx = self.x + dx
            ny = self.y + dy

            if not self.is_valid_move(maze, nx, ny):
                continue

            distance = abs(nx - target_x) + abs(ny - target_y)

            if (reverse and distance > best_distance) or \
               (not reverse and distance < best_distance):

                best_distance = distance
                best_move = (dx, dy)

        return best_move

    # --------------------------------------------------
    # RANDOM MOVE
    # --------------------------------------------------
    def random_move(self, maze):

        directions = list(self.DIRECTIONS.values())
        random.shuffle(directions)

        for dx, dy in directions:
            nx = self.x + dx
            ny = self.y + dy

            if self.is_valid_move(maze, nx, ny):
                return dx, dy

        return 0, 0

    def handle_tunnel(self, map_obj):
        if self.x < 0:
            self.x = map_obj.cols - 1
        elif self.x >= map_obj.cols:
            self.x = 0

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, screen, offset_x, offset_y):

        # Si aucune animation chargée → ne rien dessiner
        if not self.animations:
            return

        animation = self.animations.get(self.current_direction)

        # Si direction absente → prendre la première dispo
        if animation is None:
            animation = list(self.animations.values())[0]

        frame = animation.get_frame()

        screen.blit(
            frame,
            (
                offset_x + self.x * self.tile_size,
                offset_y + self.y * self.tile_size
            )
        )

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------
    def reset_position(self):
        self.x = self.spawn_x
        self.y = self.spawn_y

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.current_direction = "left"