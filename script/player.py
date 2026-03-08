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
        # POSITION / SPAWN
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
        self.death_timer = 0
        self.death_duration = 120
        self.death_sound_played = False

        # =========================
        # SPRITES / ANIMATIONS
        # =========================
        pac_folder = os.path.join(base_dir, "assets", "sprites", "Pac-Man")

        self.directions = ["RIGHT", "LEFT", "UP", "DOWN"]
        self.animations = {}

        # Charger les animations pour chaque direction
        for d in self.directions:
            folder = os.path.join(pac_folder, d.lower())
            if os.path.exists(folder):
                self.animations[d] = Animation(folder, tile_size, speed=8, loop=True)
            else:
                print(f"[Warning] Animation folder missing: {folder}")

        # Animation de mort (ne loop pas)
        death_folder = os.path.join(pac_folder, "death")
        if os.path.exists(death_folder):
            self.death_animation = Animation(death_folder, tile_size, speed=10, loop=False)
        else:
            print(f"[Warning] Death animation folder missing: {death_folder}")
            self.death_animation = None

    # ==================================================
    # INPUT / MOVEMENT
    # ==================================================
    def player_move(self):
        """
        Lit les touches et définit la prochaine direction
        ainsi que la direction actuelle pour l'animation.
        """
        keys = pygame.key.get_pressed()
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

    # ==================================================
    # ANIMATION
    # ==================================================
    def update_animation(self):
        """
        Met à jour l'animation du joueur en fonction de sa direction et de son mouvement.
        Reset sur la première frame si immobile.
        """
        anim = self.animations.get(self.direction)
        if anim:
            if self.dx != 0 or self.dy != 0 or anim.timer > 0:
                anim.update()
            else:
                anim.current_frame = 0
                anim.timer = 0

    # ==================================================
    # COLLISION / MOUVEMENT
    # ==================================================
    def can_move(self, dx, dy, game_map):
        """
        Vérifie si le joueur peut se déplacer dans la direction dx, dy
        sans rencontrer de mur.
        """
        if dx == 0 and dy == 0:
            return True

        size = self.tile_size
        half = size / 2

        next_x = self.x + dx * self.speed
        next_y = self.y + dy * self.speed

        grid_x = int((next_x + half) // size)
        grid_y = int((next_y + half) // size)

        # Si hors de la map, considérer libre (portails gérés ailleurs)
        if grid_x < 0 or grid_x >= game_map.width:
            return True
        if grid_y < 0 or grid_y >= game_map.height:
            return True

        return not game_map.is_wall(grid_x, grid_y)

    def reset_position(self):
        """
        Réinitialise le joueur à sa position de spawn.
        Remet les directions, vitesse et état de mort à zéro.
        """
        self.grid_x = self.spawn_x
        self.grid_y = self.spawn_y

        self.x = self.grid_x * self.tile_size
        self.y = self.grid_y * self.tile_size

        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.direction = "RIGHT"

        self.is_dead = False
        self.death_sound_played = False

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, surface, offset_x, offset_y):
        """
        Dessine le joueur à l'écran.
        Gère le clignotement si invincible ou mort.
        Centrage du sprite sur la tile.
        """
        if self.game_over:
            return

        # =========================
        # BLINK: invincibility ou mort
        # =========================
        blink_timer = 5  # change la vitesse du clignotement
        if (self.invincible or self.is_dead) and (
                (self.invincible_timer if self.invincible else self.death_timer) // blink_timer) % 2 == 0:
            # ne rien dessiner pour créer l'effet clignotant
            return

        # =========================
        # CHOOSE FRAME
        # =========================
        if self.is_dead:
            frame = self.death_animation.get_frame()  # ne pas update ici, update déjà fait dans update()
        else:
            anim = self.animations.get(self.direction)
            if anim:
                frame = anim.get_frame()  # ne pas update ici, update déjà fait dans update()
            else:
                return  # fallback si aucune animation

        # =========================
        # DRAW (centré sur la tile)
        # =========================
        frame_width, frame_height = frame.get_size()
        draw_x = offset_x + int(self.x + self.tile_size / 2 - frame_width / 2)
        draw_y = offset_y + int(self.y + self.tile_size / 2 - frame_height / 2)

        surface.blit(frame, (draw_x, draw_y))

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, game_map):
        """
        Met à jour l'état du joueur pour un tick de jeu :
        - Gestion de la mort et game over
        - Lecture des touches et mouvement
        - Collision mur
        - Portails horizontaux/verticaux
        - Mise à jour de la grille
        - Collecte de dots et power pellets
        - Mise à jour des timers (puissance et invincibilité)
        - Mise à jour de l'animation
        """
        # -------------------------
        # GAME OVER / DEATH
        # -------------------------
        if self.is_dead:
            if not self.death_sound_played:
                pygame.mixer.stop()
                self.audio.play_death()
                self.death_sound_played = True

            if self.death_animation:
                self.death_animation.update()

            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.death_timer = 0
                self.reset_position()
                if self.lives <= 0:
                    self.game_over = True
            return  # bloque le reste pendant la mort

        if self.game_over:
            return

        # -------------------------
        # INPUT / PLAYER MOVE
        # -------------------------
        self.player_move()  # lit les touches et définit next_dx / next_dy et direction

        # -------------------------
        # APPLY NEW DIRECTION IF POSSIBLE
        # -------------------------
        if self.can_move(self.next_dx, self.next_dy, game_map):
            self.dx = self.next_dx
            self.dy = self.next_dy

        # -------------------------
        # COLLISION WALL
        # -------------------------
        if not self.can_move(self.dx, self.dy, game_map):
            self.dx = 0
            self.dy = 0

        # -------------------------
        # MOVE PLAYER
        # -------------------------
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # -------------------------
        # PORTAL HANDLING
        # -------------------------
        self.handle_portal(game_map)

        # -------------------------
        # UPDATE GRID AFTER MOVE
        # -------------------------
        self.update_grid_position()

        # -------------------------
        # DOTS / POWER PELLETS
        # -------------------------
        result = game_map.eat_dot(self.grid_x, self.grid_y)
        if result == "dot":
            self.score += 10
            self.audio.play_chomp()
        elif result == "power":
            self.score += 50
            self.activate_power_mode()
            if hasattr(self.audio, "play_power"):
                self.audio.play_power()

        # -------------------------
        # TIMERS
        # -------------------------
        self.update_timers()

        # -------------------------
        # ANIMATION
        # -------------------------
        self.update_animation()

    # ==================================================
    # UPDATE GRID POSITION
    # ==================================================
    def update_grid_position(self):
        """
        Convertit la position pixel du joueur en coordonnées de la grille.
        """
        center_x = self.x + self.tile_size / 2
        center_y = self.y + self.tile_size / 2
        self.grid_x = int(center_x // self.tile_size)
        self.grid_y = int(center_y // self.tile_size)

    # ==================================================
    # PORTAL HANDLING
    # ==================================================
    def handle_portal(self, game_map):
        """
        Téléporte le joueur si il sort des limites de la map.
        Fonctionne pour portails horizontaux et verticaux.
        Ne téléporte que si la case de sortie n'est pas un mur.
        """
        size = self.tile_size

        # Limites horizontales
        if self.x < 0:
            target_x = (game_map.cols - 1) * size
            grid_x = int((target_x + size / 2) // size)
            if not game_map.is_wall(grid_x, self.grid_y):
                self.x = target_x
                self.grid_x = grid_x

        elif self.x + size > game_map.cols * size:
            target_x = 0
            grid_x = int((target_x + size / 2) // size)
            if not game_map.is_wall(grid_x, self.grid_y):
                self.x = target_x
                self.grid_x = grid_x

        # Limites verticales
        if self.y < 0:
            target_y = (game_map.rows - 1) * size
            grid_y = int((target_y + size / 2) // size)
            if not game_map.is_wall(self.grid_x, grid_y):
                self.y = target_y
                self.grid_y = grid_y

        elif self.y + size > game_map.rows * size:
            target_y = 0
            grid_y = int((target_y + size / 2) // size)
            if not game_map.is_wall(self.grid_x, grid_y):
                self.y = target_y
                self.grid_y = grid_y

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
            if abs(ghost.x - self.x) < self.tile_size * 0.6 and abs(ghost.y - self.y) < self.tile_size * 0.6:
                if self.power_mode:
                    if getattr(ghost, "is_boss", False):
                        ghost.take_damage(1)
                        self.score += 200
                    else:
                        ghost.reset()
                        self.score += 100
                elif not self.invincible:
                    self.lives -= 1
                    self.is_dead = True
                    self.death_animation.reset()
                    self.death_timer = 0
                    self.dx = 0
                    self.dy = 0
                    self.death_sound_played = False
                    self.invincible = True
                    self.invincible_timer = self.invincible_duration
                    break

    # ==================================================
    # UTILS
    # ==================================================
    def pixel_to_grid(self, x, y):
        return int(x // self.tile_size), int(y // self.tile_size)
