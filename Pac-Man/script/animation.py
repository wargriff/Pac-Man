import os
import pygame


class Animation:
    def __init__(self, folder_path, tile_size, speed=8):

        self.frames = []
        self.speed = speed
        self.timer = 0
        self.current_frame = 0

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Dossier introuvable : {folder_path}")

        files = sorted([
            f for f in os.listdir(folder_path)
            if f.endswith(".png")
        ])

        for file in files:
            img = pygame.image.load(
                os.path.join(folder_path, file)
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                (tile_size, tile_size)
            )

            self.frames.append(img)

        if not self.frames:
            raise ValueError(f"Aucune image trouvée dans {folder_path}")

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.current_frame = (
                self.current_frame + 1
            ) % len(self.frames)

    def get_frame(self):
        return self.frames[self.current_frame]