import os
import pygame
from script.animation import Animation


class Player:

    def __init__(self, x, y, tile_size, audio, base_dir):

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
        self.audio = audio
        self.direction = "RIGHT"
        self.score = 0

        # ----------------------------------
        # LIFE & STATE SYSTEM
        # ----------------------------------

        self.max_lives = 3
        self.lives = self.max_lives

        # ----- Player states -----
        self.is_dead = False
        self.game_over = False
        self.respawning = False

        # ----- Death management -----
        self.death_sound_played = False
        self.death_timer = 0
        self.death_duration = 60  # frames avant respawn (si tu veux délai)

        # ----- Invincibility -----
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 120  # ~2 seczzzzzzzz

        # ----------------------------------
        # POWER MODE
        # ----------------------------------
        self.power_mode = False
        self.power_timer = 0
        self.power_duration = 300  # ~5 sec

        # ----------------------------------
        # MOVEMENT
        # ----------------------------------
        self.move_timer = 0
        self.speed = 6

        # ----------------------------------
        # ANIMATIONS
        # ----------------------------------

        pac_folder = os.path.abspath(
            os.path.join(base_dir, "assets", "sprites", "Pac-Man")
        )

        self.animations = {
            "RIGHT": Animation(os.path.join(pac_folder, "right"), tile_size, 6),
            "LEFT": Animation(os.path.join(pac_folder, "left"), tile_size, 6),
            "UP": Animation(os.path.join(pac_folder, "up"), tile_size, 6),
            "DOWN": Animation(os.path.join(pac_folder, "down"), tile_size, 6),
        }

        # Animation mort
        self.death_animation = Animation(
            os.path.join(pac_folder, "death"),
            tile_size,
            6
        )
    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, game_map):

        # ==========================
        # GAME OVER → blocage total
        # ==========================
        if self.game_over:
            return

        # ==========================
        # MORT → animation
        # ==========================
        if self.is_dead:

            if not self.death_sound_played:
                self.audio.play_death()
                self.death_sound_played = True

            self.death_animation.update()

            # Fin animation
            if self.death_animation.current_frame == len(self.death_animation.frames) - 1:

                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.is_dead = False
                    self.invincible = True
                    self.invincible_timer = self.invincible_duration
                    self.reset_position()

            return

        # ==========================
        # INPUT
        # ==========================
        keys = pygame.key.get_pressed()

        wanted_dx, wanted_dy = 0, 0
        wanted_dir = self.direction

        if keys[pygame.K_q]:
            wanted_dx, wanted_dy = -1, 0
            wanted_dir = "LEFT"
        elif keys[pygame.K_d]:
            wanted_dx, wanted_dy = 1, 0
            wanted_dir = "RIGHT"
        elif keys[pygame.K_z]:
            wanted_dx, wanted_dy = 0, -1
            wanted_dir = "UP"
        elif keys[pygame.K_s]:
            wanted_dx, wanted_dy = 0, 1
            wanted_dir = "DOWN"

        # ==========================
        # TIMERS
        # ==========================
        self.update_timers()

        self.move_timer += 1
        if self.move_timer < self.speed:
            self.animations[self.direction].update()
            return

        self.move_timer = 0

        # ==========================
        # DIRECTION CHECK
        # ==========================
        test_x = self.x + wanted_dx
        test_y = self.y + wanted_dy

        if not game_map.is_wall(test_x, test_y):
            self.direction = wanted_dir
            dx, dy = wanted_dx, wanted_dy
        else:
            dx, dy = self.get_current_direction_vector()

        new_x = self.x + dx
        new_y = self.y + dy

        # ==========================
        # TUNNEL WRAP AVANT WALL CHECK
        # ==========================

        # Horizontal wrap
        if new_x < 0:
            new_x = game_map.cols - 1
        elif new_x >= game_map.cols:
            new_x = 0

        # Vertical wrap
        if new_y < 0:
            new_y = game_map.rows - 1
        elif new_y >= game_map.rows:
            new_y = 0

        # ==========================
        # MOUVEMENT
        # ==========================
        if not game_map.is_wall(new_x, new_y):

            self.x = new_x
            self.y = new_y

            result = game_map.eat_dot(self.x, self.y)

            if result == "dot":
                self.score += 10
                self.audio.play_chomp()

            elif result == "power":
                self.score += 50
                self.audio.play_eatfruit()
                self.activate_power_mode()

        # ==========================
        # ANIMATION
        # ==========================
        self.animations[self.direction].update()

    def get_current_direction_vector(self):
        if self.direction == "LEFT":
            return -1, 0
        elif self.direction == "RIGHT":
            return 1, 0
        elif self.direction == "UP":
            return 0, -1
        elif self.direction == "DOWN":
            return 0, 1
        return 0, 0

    # ==================================================
    # POWER MODE
    # ==================================================
    def activate_power_mode(self):
        self.power_mode = True
        self.power_timer = self.power_duration

    # ==================================================
    # TIMER UPDATE
    # ==================================================
    def update_timers(self):

        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    # ==================================================
    # COLLISION WITH GHOST
    # ==================================================
    def check_collision(self, ghosts):

        if self.is_dead or self.game_over:
            return

        for ghost in ghosts:

            if ghost.x == self.x and ghost.y == self.y:

                # Power mode → on attaque
                if self.power_mode:

                    if ghost.is_boss:
                        ghost.take_damage(1)
                        self.score += 200
                    else:
                        ghost.reset()
                        self.score += 100

                # Sinon → mort
                elif not self.invincible:

                    self.lives -= 1
                    self.is_dead = True
                    self.death_sound_played = False

                    # Reset animation
                    self.death_animation.current_frame = 0
                    self.death_animation.timer = 0

                    break

    # ==================================================
    # RESET POSITION
    # ==================================================
    def reset_position(self):
        self.x = self.spawn_x
        self.y = self.spawn_y

    def handle_tunnel(self, game_map):

        if self.y == game_map.rows // 2:

            if self.x < 0:
                self.x = game_map.cols - 1

            elif self.x >= game_map.cols:
                self.x = 0

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, surface, offset_x, offset_y):

        if self.game_over:
            return

        if self.is_dead:
            frame = self.death_animation.get_frame()
        else:
            frame = self.animations[self.direction].get_frame()

        if self.invincible and (self.invincible_timer % 10 < 5):
            return

        surface.blit(
            frame,
            (
                offset_x + self.x * self.tile_size,
                offset_y + self.y * self.tile_size
            )
        )