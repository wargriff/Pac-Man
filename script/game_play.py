import os
import pygame

from script.map import Map
from script.render import draw_map
from script.player import Player

from script.ghost import Ghost
from script.audio import Audio

from script.utils import resource_path
from script.fruit import Fruit


class Game:

    def __init__(self, screen):

        # =============================
        # SCREEN / DIMENSIONS
        # =============================
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # =============================
        # GAME STATE
        # =============================
        self.level = 1
        self.lives = 3

        # =============================
        # MAP
        # =============================
        self.map = Map(scale=1)

        # =============================
        # SCALE AUTO (RESPONSIVE)
        # =============================
        self.HUD_RATIO = 0.07
        self.hud_height = int(self.height * self.HUD_RATIO)

        available_height = self.height - self.hud_height
        available_width = self.width

        scale_x = available_width / self.map.cols
        scale_y = available_height / self.map.rows

        self.tile_size = max(16, int(min(scale_x, scale_y)))
        self.map.tile_size = self.tile_size

        # =============================
        # SPAWN POSITIONS
        # =============================
        self.PLAYER_SPAWN = self.find_player_spawn()

        print("PLAYER SPAWN:", self.PLAYER_SPAWN)
        print("TILE:", self.map.maze[self.PLAYER_SPAWN[1]][self.PLAYER_SPAWN[0]])

        # =============================
        # BASE DIRECTORY
        # =============================
        self.BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        # =============================
        # AUDIO
        # =============================
        self.audio = Audio()
        self.audio.play_start()

        # =============================
        # PLAYER
        # =============================
        self.player = Player(
            self.PLAYER_SPAWN[0],
            self.PLAYER_SPAWN[1],
            self.tile_size,
            self.audio,
            self.BASE_DIR
        )

        # =============================
        # GHOST CONFIG
        # =============================
        self.ghost_config = [
            (1, 14, 10, "Blinky"),
            (3, 13, 10, "Pinky"),
            (5, 15, 10, "Inky"),
            (7, 14, 9, "Clyde"),
        ]

        self.ghosts = []

        # =============================
        # FRUIT SYSTEM
        # =============================
        self.fruit_spawn_count = 0
        self.fruit = None

        # =============================
        # UI
        # =============================
        self.hud_font = pygame.font.SysFont("Arial", 22)
        self.font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", 28)

        # =============================
        # CREATE FIRST LEVEL
        # =============================
        self.create_level()

        # =============================
        # GAME OVER
        # =============================
        self.game_over = False

    # ==================================================
    # CREATE LEVEL
    # ==================================================
    def create_level(self):

        # =============================
        # RESET MAP
        # =============================
        self.map.regenerate()

        # =============================
        # RESET PLAYER
        # =============================
        self.player.reset_position()
        self.player.invincible = False
        self.player.power_mode = False

        # =============================
        # RESET FRUIT SYSTEM
        # =============================
        self.fruit_spawn_count = 0
        self.fruit = Fruit(self.level, self.map)

        # Compte réel des dots du niveau
        self.initial_dots = sum(
            tile in (".", "o")
            for row in self.map.maze
            for tile in row
        )

        # =============================
        # DIFFICULTÉ PROGRESSIVE
        # =============================

        # La vitesse diminue (plus rapide) avec le niveau
        base_speed = max(14 - self.level, 5)

        # Bonus tous les 5 niveaux
        if self.level % 5 == 0:
            base_speed = max(base_speed - 1, 3)

        # =============================
        # RESET GHOSTS
        # =============================
        self.ghosts = []

        for level_required, x, y, name in self.ghost_config:

            if self.level >= level_required:
                ghost_folder = resource_path(os.path.join("assets", "sprites", name))

                ghost = Ghost(x,y,ghost_folder,self.map.tile_size,base_speed)

                self.ghosts.append(ghost)

                base_speed = max(12 - (self.level // 2), 4)

    def find_player_spawn(self):

        # centre théorique de la map
        center_x = self.map.cols // 2
        center_y = self.map.rows // 2

        # si le centre n'est pas un mur → parfait
        if not self.map.is_wall(center_x, center_y):
            return center_x, center_y

        # sinon on cherche autour du centre
        radius = 1

        while radius < max(self.map.cols, self.map.rows):

            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):

                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x < self.map.cols and 0 <= y < self.map.rows:

                        if not self.map.is_wall(x, y):
                            return x, y

            radius += 1

        # fallback ultime
        return 1, 1

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        if self.game_over:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                self.restart_game()
            return

        # =============================
        # UPDATE PLAYER
        # =============================
        self.player.update(self.map)

        # =============================
        # UPDATE GHOSTS
        # =============================
        for ghost in self.ghosts:
            ghost.update(self.map, self.player.grid_x, self.player.grid_y)

        # =============================
        # COLLISIONS PLAYER / GHOSTS
        # =============================
        for ghost in self.ghosts:

            # ignore ghost en respawn
            if ghost.spawn_delay > 0:
                continue

            if (ghost.x, ghost.y) == (self.player.grid_x, self.player.grid_y):

                # POWER MODE → mange ghost
                if self.player.power_mode:
                    ghost.reset()
                    self.player.score += 200
                    self.audio.play_chomp()
                    continue

                # PLAYER HIT
                if not self.player.invincible:

                    self.player.lives -= 1
                    self.player.is_dead = True

                    if self.player.lives <= 0:
                        self.player.game_over = True
                        self.game_over = True
                        return

                    # reset positions
                    self.player.reset_position()

                    for g in self.ghosts:
                        g.reset()

                    return

        # =============================
        # CHECK FIN DE LEVEL
        # =============================
        if not self.map.remaining_dots():
            self.level += 1
            self.create_level()
            return

        # =============================
        # FRUIT SYSTEM
        # =============================
        total_remaining = sum(
            tile in (".", "o")
            for row in self.map.maze
            for tile in row
        )

        if not hasattr(self, "initial_dots"):
            self.initial_dots = total_remaining

        progress = 1 - (total_remaining / self.initial_dots)

        if self.fruit_spawn_count == 0 and progress >= 0.3:
            self.fruit.spawn()
            self.fruit_spawn_count += 1

        elif self.fruit_spawn_count == 1 and progress >= 0.7:
            self.fruit.spawn()
            self.fruit_spawn_count += 1

        self.fruit.update()

        # =============================
        # COLLISION PLAYER / FRUIT
        # =============================
        if self.fruit.visible:

            if (self.player.grid_x, self.player.grid_y) == (self.fruit.x, self.fruit.y):
                self.player.score += self.fruit.score_value
                self.fruit.visible = False
                self.audio.play_eatghost()

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):
        # ================= SCREEN =================
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.screen.fill((0, 0, 0))

        # ================= HUD =================
        hud_height = int(screen_height * 0.07)
        pygame.draw.rect(self.screen, (15, 15, 35), (0, 0, screen_width, hud_height))

        # Texte HUD
        score_text = self.hud_font.render(f"Score: {self.player.score}", True, (255, 255, 0))
        lives_text = self.hud_font.render(f"Vies: {self.player.lives}", True, (255, 255, 255))
        level_text = self.hud_font.render(f"Niveau: {self.level}", True, (0, 255, 255))

        text_y = hud_height // 2 - score_text.get_height() // 2

        # Score à gauche
        self.screen.blit(score_text, (20, text_y))
        # Vies au centre
        self.screen.blit(lives_text, (screen_width // 2 - lives_text.get_width() // 2, text_y))
        # Niveau à droite
        self.screen.blit(level_text, (screen_width - level_text.get_width() - 20, text_y))

        # ================= MAP CENTERING =================
        map_pixel_width = self.map.cols * self.map.tile_size
        map_pixel_height = self.map.rows * self.map.tile_size

        offset_x = (screen_width - map_pixel_width) // 2
        offset_y = hud_height + (screen_height - hud_height - map_pixel_height) // 2

        # Draw fruit
        if hasattr(self, 'fruit') and self.fruit:
            self.fruit.draw(self.screen, offset_x, offset_y, self.map.tile_size)

        # ================= DRAW MAP =================
        for y in range(self.map.rows):
            for x in range(self.map.cols):
                tile = self.map.maze[y][x]
                px = offset_x + x * self.map.tile_size
                py = offset_y + y * self.map.tile_size

                if tile == "#":
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (px, py, self.map.tile_size, self.map.tile_size))
                elif tile == ".":
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                       (px + self.map.tile_size // 2, py + self.map.tile_size // 2), 3)
                elif tile == "o":
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                       (px + self.map.tile_size // 2, py + self.map.tile_size // 2), 6)

        # ================= PLAYER =================
        self.player.draw(self.screen, offset_x, offset_y)

        # ================= GHOSTS =================
        for ghost in self.ghosts:
            ghost.draw(self.screen, offset_x, offset_y)

        # ================= GAME OVER =================
        if self.game_over:
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.small_font.render("Press R to Restart", True, (255, 255, 255))

            self.screen.blit(game_over_text,
                             (screen_width // 2 - game_over_text.get_width() // 2,
                              screen_height // 2 - 40))
            self.screen.blit(restart_text,
                             (screen_width // 2 - restart_text.get_width() // 2,
                              screen_height // 2 + 10))

    # ==================================================
    # RESET GAME
    # ==================================================
    def reset_full_game(self):
        self.level = 1
        self.player.lives = self.player.max_lives
        self.player.score = 0
        self.game_over = False
        self.create_level()

    # ==================================================
    # RESTART GAME
    # ==================================================
    def restart_game(self):
        self.level = 1
        self.player.score = 0
        self.player.lives = self.player.max_lives
        self.player.game_over = False
        self.player.is_dead = False
        self.game_over = False
        self.create_level()

    # ==================================================
    # RESIZE
    # ==================================================
    def resize(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.get_surface()

        hud_height = int(self.height * 0.07)
        available_width = self.width
        available_height = self.height - hud_height

        scale_x = available_width / self.map.cols
        scale_y = available_height / self.map.rows
        tile = int(min(scale_x, scale_y))

        # Update tile size
        self.map.tile_size = tile
        self.player.tile_size = tile
        self.player.x = self.player.grid_x * tile
        self.player.y = self.player.grid_y * tile

        for ghost in self.ghosts:
            ghost.tile_size = tile
            ghost.x = ghost.grid_x * tile
            ghost.y = ghost.grid_y * tile

    # ==================================================
    # RESET GAME
    # ==================================================
    def reset_full_game(self):
        self.level = 1
        self.lives = 3
        self.player.score = 0
        self.create_level()

    # ==================================================
    # RESTART GAME
    # ==================================================
    def restart_game(self):

        self.level = 1
        self.player.score = 0
        self.player.lives = self.player.max_lives
        self.player.game_over = False
        self.player.is_dead = False

        self.game_over = False

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

        # MAP
        self.map.tile_size = tile

        # PLAYER
        self.player.tile_size = tile
        self.player.x = self.player.grid_x * tile
        self.player.y = self.player.grid_y * tile

        # GHOSTS
        for ghost in self.ghosts:
            ghost.tile_size = tile
            ghost.x = ghost.grid_x * tile
            ghost.y = ghost.grid_y * tile