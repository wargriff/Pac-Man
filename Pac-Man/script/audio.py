import pygame
import os


class Audio:

    def __init__(self, base_dir):

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.base_path = os.path.join(base_dir, "assets", "audio")

        self.sounds = {
            "start": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_beginning.wav")),
            "chomp": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_chomp.wav")),
            "death": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_death.wav")),
            "eatfruit": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_eatfruit.wav")),
            "eatghost": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_eatghost.wav")),
            "extralife": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_extrapac.wav")),
            "intermission": pygame.mixer.Sound(os.path.join(self.base_path, "pacman_intermission.wav")),
        }

        self.set_volume(0.5)

        # Timer anti spam pour chomp
        self.last_chomp_time = 0

    # ----------------------------------
    # PLAY GENERIC
    # ----------------------------------
    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # ----------------------------------
    # SAFE CHOMP (anti spam)
    # ----------------------------------
    def play_chomp(self):
        now = pygame.time.get_ticks()
        if now - self.last_chomp_time > 120:  # 120ms entre deux sons
            self.sounds["chomp"].play()
            self.last_chomp_time = now

    def play_start(self):
        self.play("start")

    def play_death(self):
        self.play("death")

    def play_eatfruit(self):
        self.play("eatfruit")

    def play_eatghost(self):
        self.play("eatghost")

    def play_extralife(self):
        self.play("extralife")

    def play_intermission(self):
        self.play("intermission")

    def set_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)