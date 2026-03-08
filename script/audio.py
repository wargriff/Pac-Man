# script/audio.py
import pygame
import os


class Audio:

    def __init__(self):

        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        pygame.mixer.set_num_channels(8)

        # chemin simple vers assets/audio
        self.base_path = os.path.join("assets", "audio")

        self.sounds = {}

        sound_files = {
            "start": "pacman_beginning.wav",
            "chomp": "pacman_chomp.wav",
            "death": "pacman_death.wav",
            "eatfruit": "pacman_eatfruit.wav",
            "eatghost": "pacman_eatghost.wav",
            "extralife": "pacman_extrapac.wav",
            "intermission": "pacman_intermission.wav",
        }

        for name, filename in sound_files.items():
            self.sounds[name] = self.load_sound(filename)

        self.volume = 0.5
        self.set_volume(self.volume)

        self.last_chomp_time = 0

    # ----------------------------------
    # SAFE SOUND LOADER
    # ----------------------------------
    def load_sound(self, filename):

        path = os.path.join(self.base_path, filename)

        if not os.path.exists(path):
            print("❌ Missing sound:", path)
            return None

        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print("❌ Sound load error:", filename, e)
            return None

    # ----------------------------------
    # PLAY GENERIC
    # ----------------------------------
    def play(self, name):

        sound = self.sounds.get(name)

        if sound:
            sound.play()

    # ----------------------------------
    # SAFE CHOMP (anti spam)
    # ----------------------------------
    def play_chomp(self):

        now = pygame.time.get_ticks()

        if now - self.last_chomp_time > 120:

            sound = self.sounds.get("chomp")

            if sound:
                sound.play()

            self.last_chomp_time = now

    # ----------------------------------
    # SPECIFIC SOUNDS
    # ----------------------------------
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

    # ----------------------------------
    # MUSIC
    # ----------------------------------
    def play_music(self, filename, loop=True):

        path = os.path.join(self.base_path, filename)

        if not os.path.exists(path):
            print("❌ Music missing:", path)
            return

        pygame.mixer.music.load(path)

        if loop:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()

    def stop_music(self):
        pygame.mixer.music.stop()

    # ----------------------------------
    # VOLUME
    # ----------------------------------
    def set_volume(self, volume):

        self.volume = max(0, min(volume, 1))

        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)

        pygame.mixer.music.set_volume(self.volume)