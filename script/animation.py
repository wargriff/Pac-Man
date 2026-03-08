# script/animation.py
import os
import pygame


class Animation:

    def __init__(self, folder_path, tile_size, speed=8, loop=True):
        self.frames = []
        self.speed = speed        # vitesse du changement de frame
        self.timer = 0
        self.current_frame = 0
        self.loop = loop
        self.finished = False

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Dossier introuvable : {folder_path}")

        # Trier les fichiers correctement même si les numéros ont des zéros initiaux
        files = sorted(
            [f for f in os.listdir(folder_path) if f.endswith(".png")],
            key=lambda x: int(x.split("_")[1].split(".")[0].lstrip("0")) if "_" in x else 0
        )

        print("Loaded frames:", files)

        for file in files:
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, (tile_size, tile_size))
            self.frames.append(img)

        if not self.frames:
            raise ValueError(f"Aucune image trouvée dans {folder_path}")

    def update(self):
        """Avancer l'animation d'une frame si nécessaire"""
        if self.finished or len(self.frames) == 0:
            return

        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            if self.loop:
                # boucle infinie
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            else:
                # animation qui se joue une seule fois
                if self.current_frame < len(self.frames) - 1:
                    self.current_frame += 1
                else:
                    self.finished = True  # animation terminée

    def reset(self):
        """Remettre l'animation au début"""
        self.current_frame = 0
        self.timer = 0
        self.finished = False

    def get_frame(self):
        """Retourne la frame actuelle"""
        if len(self.frames) == 0:
            return None
        return self.frames[self.current_frame]