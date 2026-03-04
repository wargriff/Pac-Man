import os
import pygame

from script.map import Map
from script.render import draw_map
from script.player import Player

from script.ghost import Ghost
from script.audio import Audio


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

        # Sécurité : minimum 16px pour éviter bugs
        self.tile_size = max(16, int(min(scale_x, scale_y)))

        self.map.tile_size = self.tile_size

        # =============================
        # SPAWN POSITIONS (CONST)
        # =============================
        self.PLAYER_SPAWN = (14, 23)

        # =============================
        # BASE DIRECTORY
        # =============================
        self.BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        # =============================
        # AUDIO
        # =============================
        self.audio = Audio(self.BASE_DIR)
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
        # (niveau_min, x, y, dossier_sprite)
        # =============================
        self.ghost_config = [
            (1, 14, 10, "Blinky"),
            (3, 13, 10, "Pinky"),
            (5, 15, 10, "Inky"),
            (7, 14, 9, "Clyde"),
        ]

        self.ghosts = []

        # =============================
        # FRUIT SYSTEM INIT
        # =============================
        self.fruit_spawn_count = 0
        self.fruit = None

        # =============================
        # UI
        # =============================
        self.font = pygame.font.SysFont("Arial", 22)

        # =============================
        # CREATE FIRST LEVEL
        # =============================
        self.create_level()

        # =============================
        # GAME OVER
        # =============================
        self.game_over = False
        self.font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", 28)


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
                ghost_folder = os.path.join(self.BASE_DIR,"assets","sprites",name)

                ghost = Ghost(x,y,ghost_folder,self.map.tile_size,base_speed)

                self.ghosts.append(ghost)

                base_speed = max(12 - (self.level // 2), 4)

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        if self.game_over:
            mouse_buttons = pygame.mouse.get_pressed()
            # Bouton gauche = index 0
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
            ghost.update(self.map, self.player.x, self.player.y)

        # =============================
        # COLLISIONS PLAYER / GHOSTS
        # =============================
        for ghost in self.ghosts:
            if (ghost.x, ghost.y) == (self.player.x, self.player.y):

                # Si power mode actif → player mange le ghost
                if self.player.power_mode:
                    ghost.reset_position()
                    self.player.score += 200
                    self.audio.play_chomp()
                    continue

                # Sinon player perd une vie
                if not self.player.invincible:

                    self.player.lives -= 1
                    self.player.is_dead = True

                    if self.player.lives <= 0:
                        self.player.game_over = True
                        self.game_over = True
                        return

                    # Reset positions (sans reset map)
                    self.player.reset_position()

                    for g in self.ghosts:
                        g.reset_position()

                    return  # Stop update pour éviter multi-hit

        # =============================
        # CHECK FIN DE LEVEL
        # =============================
        if not self.map.remaining_dots():
            self.level += 1
            self.create_level()
            return

        # =============================
        # FRUIT SYSTEM (30% / 70%)
        # =============================

        total_remaining = sum(
            tile in (".", "o")
            for row in self.map.maze
            for tile in row
        )

        if not hasattr(self, "initial_dots"):
            self.initial_dots = total_remaining

        progress = 1 - (total_remaining / self.initial_dots)

        # Spawn fruit à 30%
        if self.fruit_spawn_count == 0 and progress >= 0.3:
            self.fruit.spawn()
            self.fruit_spawn_count += 1

        # Spawn fruit à 70%
        elif self.fruit_spawn_count == 1 and progress >= 0.7:
            self.fruit.spawn()
            self.fruit_spawn_count += 1

        self.fruit.update()

        # =============================
        # COLLISION PLAYER / FRUIT
        # =============================
        if self.fruit.visible:
            if (self.player.x, self.player.y) == (self.fruit.x, self.fruit.y):
                self.player.score += self.fruit.score_value
                self.fruit.visible = False
                self.audio.play_eatghost()

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        # Dimensions écran
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

        # Textes HUD
        score_text = self.font.render(
            f"Score: {self.player.score}",
            True,
            (255, 255, 0)
        )

        lives_text = self.font.render(
            f"Vies: {self.player.lives}",  # ✅ CORRIGÉ ICI
            True,
            (255, 255, 255)
        )

        level_text = self.font.render(
            f"Niveau: {self.level}",
            True,
            (0, 255, 255)
        )

        # Alignement vertical centré dans le HUD
        text_y = hud_height // 2 - score_text.get_height() // 2

        # Score à gauche
        self.screen.blit(score_text, (20, text_y))

        # Vies au centre
        self.screen.blit(
            lives_text,
            (screen_width // 2 - lives_text.get_width() // 2, text_y)
        )

        # Niveau à droite
        self.screen.blit(
            level_text,
            (screen_width - level_text.get_width() - 20, text_y)
        )

        # ================= MAP CENTERING =================

        map_pixel_width = self.map.cols * self.map.tile_size
        map_pixel_height = self.map.rows * self.map.tile_size

        offset_x = (screen_width - map_pixel_width) // 2
        offset_y = hud_height + (
                (screen_height - hud_height - map_pixel_height) // 2
        )

        self.fruit.draw(self.screen, offset_x, offset_y, self.map.tile_size)

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

        if self.game_over:
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.small_font.render("Press R to Restart", True, (255, 255, 255))

            self.screen.blit(
                game_over_text,
                (
                    self.screen.get_width() // 2 - game_over_text.get_width() // 2,
                    self.screen.get_height() // 2 - 40
                )
            )

            self.screen.blit(
                restart_text,
                (
                    self.screen.get_width() // 2 - restart_text.get_width() // 2,
                    self.screen.get_height() // 2 + 10
                )
            )

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

        # Met à jour map
        self.map.tile_size = tile
        self.map.update_dimensions()

        # Met à jour player
        self.player.tile_size = tile

        # Met à jour ghosts
        for ghost in self.ghosts:
            ghost.tile_size = tile