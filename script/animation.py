# script/animation.py

import os
import pygame
from script.utils.resource import resource_path



# ==========================================================
# ASSET MANAGER
# ==========================================================

class AssetManager:

    _images = {}

    @classmethod
    def image(cls, path):

        if path not in cls._images:

            full = resource_path(path)
            cls._images[path] = pygame.image.load(full).convert_alpha()

        return cls._images[path]


# ==========================================================
# ANIMATION
# ==========================================================

class Animation:

    def __init__(self, folder_path, tile_size, speed=8, loop=True):

        self.frames = []
        self.speed = speed
        self.timer = 0
        self.current_frame = 0
        self.loop = loop
        self.finished = False

        # chemin absolu compatible PyInstaller
        folder = resource_path(folder_path)

        if not os.path.exists(folder):
            raise FileNotFoundError(f"Dossier introuvable : {folder}")

        # tri correct des frames
        files = sorted(
            [f for f in os.listdir(folder) if f.endswith(".png")],
            key=self._frame_sort
        )

        print("Loaded frames:", files)

        for file in files:

            img = AssetManager.image(f"{folder_path}/{file}")
            img = pygame.transform.scale(img, (tile_size, tile_size))

            self.frames.append(img)

        if not self.frames:
            raise ValueError(f"Aucune image trouvée dans {folder}")

    # ==========================================================
    # TRI DES FRAMES
    # ==========================================================

    def _frame_sort(self, filename):

        try:
            return int(filename.split("_")[1].split(".")[0])
        except:
            return 0

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self):

        if self.finished or not self.frames:
            return

        self.timer += 1

        if self.timer >= self.speed:

            self.timer = 0

            if self.loop:
                self.current_frame = (self.current_frame + 1) % len(self.frames)

            else:
                if self.current_frame < len(self.frames) - 1:
                    self.current_frame += 1
                else:
                    self.finished = True

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self):

        self.current_frame = 0
        self.timer = 0
        self.finished = False

    # ==========================================================
    # GET FRAME
    # ==========================================================

    def get_frame(self):

        if not self.frames:
            return None

        return self.frames[self.current_frame]