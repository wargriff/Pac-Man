import os
import pygame
from script.map import Map
from script.render import draw_map
from script.player import Player
from script.ghost import Ghost
from script.audio import Audio


class Game:

    def __init__(self, screen):

        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.level = 1
        self.lives = 3

        self.map = Map(scale=1)

        # =========================
        # SCALE AUTO
        # =========================
        hud_height = int(self.height * 0.07)

        available_height = self.height - hud_height
        available_width = self.width

        scale_x = available_width / self.map.cols
        scale_y = available_height / self.map.rows

        tile = int(min(scale_x, scale_y))
        self.map.tile_size = tile

        # =========================
        # BASE DIR
        # =========================
        self.BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # =========================
        # AUDIO
        # =========================
        self.audio = Audio(self.BASE_DIR)
        self.audio.play_start()

        # =========================
        # PLAYER (nouveau constructeur)
        # =========================
        self.player = Player(
            14,
            23,
            tile,
            self.audio,
            self.BASE_DIR
        )

        # =========================
        # GHOST CONFIG
        # =========================
        self.ghost_config = [
            (1, 14, 10, "Blinky"),
            (3, 13, 10, "Pinky"),
            (5, 15, 10, "Inky"),
            (7, 14, 9, "Clyde"),
        ]

        self.ghosts = []

        self.font = pygame.font.SysFont("Arial", 22)

        self.create_level()

    # ==================================================
    # CREATE LEVEL
    # ==================================================
    def create_level(self):

        self.map.regenerate()

        self.player.x = 14
        self.player.y = 23

        self.ghosts = []

        base_speed = max(15 - self.level, 5)

        for level_min, x, y, name in self.ghost_config:

            if self.level >= level_min:

                ghost_folder = os.path.join(
                    self.BASE_DIR,
                    "assets",
                    "sprites",
                    name
                )

                ghost = Ghost(
                    x,
                    y,
                    ghost_folder,
                    self.map.tile_size,
                    base_speed
                )

                self.ghosts.append(ghost)

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        # ===== UPDATE PLAYER =====
        self.player.update(self.map)

        # ===== UPDATE GHOSTS =====
        for ghost in self.ghosts:

            ghost.update(self.map.maze, self.player.x, self.player.y)

            # ===== COLLISION PLAYER / GHOST =====
            if (ghost.x, ghost.y) == (self.player.x, self.player.y):

                self.lives -= 1
                self.audio.play_death()

                # Reset position joueur
                self.player.x = 14
                self.player.y = 23

                # Optionnel : reset ghosts aussi
                self.create_level()

                if self.lives <= 0:
                    self.reset_full_game()

                # Important : on sort pour éviter multi-collision
                return

        # ===== CHECK FIN DE LEVEL =====
        if not self.map.remaining_dots():
            self.level += 1
            self.create_level()

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        # Dimensions réelles écran
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        self.screen.fill((0, 0, 0))

        # ================= HUD =================
        hud_height = int(screen_height * 0.07)

        pygame.draw.rect(
            self.screen,
            (15, 15, 35),
            (0, 0, screen_width, hud_height)
        )

        score_text = self.font.render(
            f"Score: {self.player.score}",
            True,
            (255, 255, 0)
        )

        lives_text = self.font.render(
            f"Vies: {self.lives}",
            True,
            (255, 255, 255)
        )

        level_text = self.font.render(
            f"Niveau: {self.level}",
            True,
            (0, 255, 255)
        )

        self.screen.blit(score_text, (20, hud_height // 3))

        self.screen.blit(
            lives_text,
            (screen_width // 2 - lives_text.get_width() // 2, hud_height // 3)
        )

        self.screen.blit(
            level_text,
            (screen_width - level_text.get_width() - 20, hud_height // 3)
        )

        # ================= MAP CENTERING =================

        map_pixel_width = self.map.cols * self.map.tile_size
        map_pixel_height = self.map.rows * self.map.tile_size

        offset_x = (screen_width - map_pixel_width) // 2
        offset_y = hud_height + (
                (screen_height - hud_height - map_pixel_height) // 2
        )

        # ================= DRAW MAP =================
        for y in range(self.map.rows):
            for x in range(self.map.cols):

                tile = self.map.maze[y][x]

                px = offset_x + x * self.map.tile_size
                py = offset_y + y * self.map.tile_size

                if tile == "#":
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 255),
                        (px, py, self.map.tile_size, self.map.tile_size)
                    )

                elif tile == ".":
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (px + self.map.tile_size // 2,
                         py + self.map.tile_size // 2),
                        3
                    )

                elif tile == "o":
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (px + self.map.tile_size // 2,
                         py + self.map.tile_size // 2),
                        6
                    )

        # ================= PLAYER =================
        self.player.draw(self.screen, offset_x, offset_y)

        # ================= GHOSTS =================
        for ghost in self.ghosts:
            ghost.draw(self.screen, offset_x, offset_y)

    # ==================================================
    # RESET GAME
    # ==================================================
    def reset_full_game(self):
        self.level = 1
        self.lives = 3
        self.player.score = 0
        self.create_level()

    # ==================================================
    # RESIZE
    # ==================================================
    def resize(self, width, height):

        self.width = width
        self.height = height
        self.screen = pygame.display.get_surface()

        hud_height = int(self.height * 0.07)

        available_height = self.height - hud_height
        available_width = self.width

        scale_x = available_width / self.map.cols
        scale_y = available_height / self.map.rows

        tile = int(min(scale_x, scale_y))

        # Met à jour map
        self.map.tile_size = tile
        self.map.update_dimensions()

        # Met à jour player
        self.player.tile_size = tile

        # Met à jour ghosts
        for ghost in self.ghosts:
            ghost.tile_size = tile