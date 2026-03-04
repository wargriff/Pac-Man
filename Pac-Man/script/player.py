import os
import pygame
from script.animation import Animation


class Player:

    def __init__(self, x, y, tile_size, audio, base_dir):

        self.x = x
        self.y = y

        self.tile_size = tile_size
        self.audio = audio
        self.direction = "RIGHT"
        self.score = 0

        # -------- Mouvement --------
        self.move_timer = 0
        self.speed = 6

        # -------- Animations --------
        pac_folder = os.path.join(base_dir, "assets", "sprites", "Pac-Man")

        self.animations = {
            "RIGHT": Animation(pac_folder, "right", tile_size, 6),
            "LEFT": Animation(pac_folder, "left", tile_size, 6),
            "UP": Animation(pac_folder, "up", tile_size, 6),
            "DOWN": Animation(pac_folder, "down", tile_size, 6),
        }

    # =========================
    # UPDATE
    # =========================
    def update(self, game_map):

        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        # -------- ZQSD --------
        if keys[pygame.K_q]:
            self.direction = "LEFT"
            dx = -1

        elif keys[pygame.K_d]:
            self.direction = "RIGHT"
            dx = 1

        elif keys[pygame.K_z]:
            self.direction = "UP"
            dy = -1

        elif keys[pygame.K_s]:
            self.direction = "DOWN"
            dy = 1

        # -------- Gestion vitesse --------
        self.move_timer += 1
        if self.move_timer < self.speed:
            self.animations[self.direction].update()
            return

        self.move_timer = 0

        new_x = self.x + dx
        new_y = self.y + dy

        # -------- Collision mur via Map --------
        if not game_map.is_wall(new_x, new_y):

            self.x = new_x
            self.y = new_y

            # -------- Mange point via Map --------
            result = game_map.eat_dot(self.x, self.y)

            if result == "dot":
                self.score += 10
                self.audio.play_chomp()

            elif result == "power":
                self.score += 50
                self.audio.play_eatfruit()

        # -------- Animation --------
        self.animations[self.direction].update()

    # =========================
    # DRAW
    # =========================
    def draw(self, surface, offset_x, offset_y):

        frame = self.animations[self.direction].get_frame()

        surface.blit(
            frame,
            (
                offset_x + self.x * self.tile_size,
                offset_y + self.y * self.tile_size
            )
        )