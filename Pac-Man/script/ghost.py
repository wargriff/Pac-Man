import random
import os
from script.animation import Animation
from script.ai import GhostAI


class Ghost:

    def __init__(self, x, y, folder_path, tile_size, speed):

        self.x = x
        self.y = y

        self.spawn_x = x
        self.spawn_y = y

        self.tile_size = tile_size
        self.speed = speed

        self.timer = 0

        # Nom du ghost = nom du dossier
        self.name = os.path.basename(folder_path)

        # Animation (2 frames auto chargées)
        self.animation = Animation(folder_path, "", tile_size, speed=10)

        # IA
        self.ai = GhostAI(self)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, maze, player_x, player_y):

        self.timer += 1

        if self.timer >= self.speed:
            self.timer = 0

            dx, dy = self.ai.update(maze, player_x, player_y)

            new_x = self.x + dx
            new_y = self.y + dy

            if 0 <= new_y < len(maze) and 0 <= new_x < len(maze[0]):
                if maze[new_y][new_x] != "#":
                    self.x = new_x
                    self.y = new_y

        # Animation toujours mise à jour
        self.animation.update()

    # --------------------------------------------------
    # IA
    # --------------------------------------------------
    def choose_direction(self, maze, player_x, player_y):

        if self.name.lower() == "blinky":
            return self.move_towards(maze, player_x, player_y)

        elif self.name.lower() == "pinky":
            return self.move_towards(maze, player_x + 2, player_y)

        elif self.name.lower() == "inky":
            if random.random() < 0.6:
                return self.move_towards(maze, player_x, player_y)
            return self.random_move(maze)

        elif self.name.lower() == "clyde":
            distance = abs(self.x - player_x) + abs(self.y - player_y)
            if distance < 5:
                return self.move_away(maze, player_x, player_y)
            return self.move_towards(maze, player_x, player_y)

        return self.random_move(maze)

    # --------------------------------------------------
    # MOVE TOWARDS
    # --------------------------------------------------
    def move_towards(self, maze, target_x, target_y):

        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        best_move = (0, 0)
        best_distance = 9999

        for dx, dy in directions:

            nx = self.x + dx
            ny = self.y + dy

            if ny < 0 or ny >= len(maze):
                continue
            if nx < 0 or nx >= len(maze[0]):
                continue
            if maze[ny][nx] == "#":
                continue

            distance = abs(nx - target_x) + abs(ny - target_y)

            if distance < best_distance:
                best_distance = distance
                best_move = (dx, dy)

        return best_move

    # --------------------------------------------------
    # MOVE AWAY
    # --------------------------------------------------
    def move_away(self, maze, target_x, target_y):

        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        best_move = (0, 0)
        best_distance = -1

        for dx, dy in directions:

            nx = self.x + dx
            ny = self.y + dy

            if ny < 0 or ny >= len(maze):
                continue
            if nx < 0 or nx >= len(maze[0]):
                continue
            if maze[ny][nx] == "#":
                continue

            distance = abs(nx - target_x) + abs(ny - target_y)

            if distance > best_distance:
                best_distance = distance
                best_move = (dx, dy)

        return best_move

    # --------------------------------------------------
    # RANDOM MOVE
    # --------------------------------------------------
    def random_move(self, maze):

        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(directions)

        for dx, dy in directions:

            nx = self.x + dx
            ny = self.y + dy

            if ny < 0 or ny >= len(maze):
                continue
            if nx < 0 or nx >= len(maze[0]):
                continue
            if maze[ny][nx] != "#":
                return dx, dy

        return 0, 0

        # --------------------------------------------------
        # DRAW
        # --------------------------------------------------

    def draw(self, screen, offset_x, offset_y):

        frame = self.animation.get_frame()

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

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y