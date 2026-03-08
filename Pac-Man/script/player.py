import os
import pygame
from script.animation import Animation


class Player:

    def __init__(self, x, y, tile_size, audio, base_dir):

        # =========================
        # CONFIG
        # =========================
        self.tile_size = tile_size
        self.audio = audio

        # =========================
        # POSITION
        # =========================
        self.spawn_x = x
        self.spawn_y = y

        self.grid_x = x
        self.grid_y = y

        self.x = x * tile_size
        self.y = y * tile_size

        # =========================
        # MOVEMENT
        # =========================
        self.dx = 0
        self.dy = 0

        self.next_dx = 0
        self.next_dy = 0

        self.speed = 2
        self.direction = "RIGHT"

        # =========================
        # GAME STATS
        # =========================
        self.score = 0

        self.max_lives = 3
        self.lives = self.max_lives

        self.is_dead = False
        self.game_over = False

        # =========================
        # POWER / INVINCIBILITY
        # =========================
        self.power_mode = False
        self.power_timer = 0
        self.power_duration = 300

        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 120

        # =========================
        # DEATH
        # =========================
        self.death_sound_played = False

        # =========================
        # SPRITES / ANIMATIONS
        # =========================
        pac_folder = os.path.join(base_dir, "assets", "sprites", "Pac-Man")

        directions = ["RIGHT", "LEFT", "UP", "DOWN"]

        self.animations = {
            d: Animation(os.path.join(pac_folder, d.lower()), tile_size, 6)
            for d in directions
        }

        self.death_animation = Animation(
            os.path.join(pac_folder, "death"),
            tile_size,
            6
        )

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self, game_map):

        if self.game_over or self.is_dead:
            return

        self.update_timers()

        keys = pygame.key.get_pressed()

        # =========================
        # INPUT
        # =========================
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.next_dx, self.next_dy = -1, 0
            self.direction = "LEFT"

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.next_dx, self.next_dy = 1, 0
            self.direction = "RIGHT"

        elif keys[pygame.K_z] or keys[pygame.K_UP]:
            self.next_dx, self.next_dy = 0, -1
            self.direction = "UP"

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.next_dx, self.next_dy = 0, 1
            self.direction = "DOWN"

        # =========================
        # POSITIONS
        # =========================
        half = self.tile_size // 2

        center_x = self.grid_x * self.tile_size + half
        center_y = self.grid_y * self.tile_size + half

        player_center_x = self.x + half
        player_center_y = self.y + half

        tolerance = self.speed

        at_center = (
                abs(player_center_x - center_x) <= tolerance
                and abs(player_center_y - center_y) <= tolerance
        )

        # =========================
        # TURN SYSTEM
        # =========================
        if at_center:

            # snap parfait au centre
            self.x = center_x - half
            self.y = center_y - half

            # tentative de virage
            test_x = self.grid_x + self.next_dx
            test_y = self.grid_y + self.next_dy

            if not game_map.is_wall(test_x, test_y):
                self.dx = self.next_dx
                self.dy = self.next_dy

        # =========================
        # CALCUL PROCHAINE POSITION
        # =========================
        next_x = self.x + self.dx * self.speed
        next_y = self.y + self.dy * self.speed

        next_center_x = next_x + half
        next_center_y = next_y + half

        grid_x = int(next_center_x // self.tile_size)
        grid_y = int(next_center_y // self.tile_size)

        # =========================
        # COLLISION MUR
        # =========================
        if not game_map.is_wall(grid_x, grid_y):

            self.x = next_x
            self.y = next_y

            self.grid_x = int((self.x + half) // self.tile_size)
            self.grid_y = int((self.y + half) // self.tile_size)

        else:
            # stop si mur
            self.dx = 0
            self.dy = 0

        # =========================
        # MAP INTERACTION
        # =========================
        result = game_map.eat_dot(self.grid_x, self.grid_y)

        if result == "dot":
            self.score += 10
            self.audio.play_chomp()

        elif result == "power":
            self.score += 50
            self.activate_power_mode()

        # =========================
        # ANIMATION
        # =========================
        anim = self.animations.get(self.direction)

        if anim:
            anim.update()

    # ==================================================
    # POWER MODE
    # ==================================================

    def activate_power_mode(self):

        self.power_mode = True
        self.power_timer = self.power_duration

    # ==================================================
    # TIMERS
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
    # COLLISION
    # ==================================================

    def check_collision(self, ghosts):

        if self.is_dead or self.game_over:
            return

        for ghost in ghosts:

            if ghost.grid_x == self.grid_x and ghost.grid_y == self.grid_y:

                if self.power_mode:

                    if ghost.is_boss:
                        ghost.take_damage(1)
                        self.score += 200
                    else:
                        ghost.reset()
                        self.score += 100

                elif not self.invincible:

                    self.lives -= 1
                    self.is_dead = True
                    self.death_sound_played = False

                    self.death_animation.current_frame = 0
                    self.death_animation.timer = 0

                    break

    def pixel_to_grid(self, x, y):
        return int(x // self.tile_size), int(y // self.tile_size)

    # ==================================================
    # RESET
    # ==================================================

    def reset_position(self):

        self.grid_x = self.spawn_x
        self.grid_y = self.spawn_y

        self.x = self.spawn_x * self.tile_size
        self.y = self.spawn_y * self.tile_size

        # reset mouvement
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.direction = "RIGHT"

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self, surface, offset_x, offset_y):

        if self.game_over:
            return

        # =========================
        # INVINCIBILITY BLINK
        # =========================
        if self.invincible and (self.invincible_timer % 10 < 5):
            return

        # =========================
        # CHOOSE FRAME
        # =========================
        if self.is_dead:
            frame = self.death_animation.get_frame()
        else:
            anim = self.animations.get(self.direction)

            if anim:
                frame = anim.get_frame()
            else:
                return

        # =========================
        # DRAW (PIXEL POSITION)
        # =========================
        draw_x = offset_x + int(self.x)
        draw_y = offset_y + int(self.y)

        surface.blit(frame, (draw_x, draw_y))