import sys
from pathlib import Path


# ==========================================================
# BASE PATH (cached)
# ==========================================================

_BASE_PATH: Path | None = None


def get_base_path() -> Path:
    """
    Retourne le dossier racine du projet ou du bundle PyInstaller.
    """

    global _BASE_PATH

    if _BASE_PATH is not None:
        return _BASE_PATH

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        _BASE_PATH = Path(sys._MEIPASS)
    else:
        _BASE_PATH = Path(__file__).resolve().parents[2]

    return _BASE_PATH


# ==========================================================
# RESOURCE PATH
# ==========================================================

def resource_path(relative: str | Path) -> Path:
    """
    Retourne le chemin absolu d'une ressource.

    Compatible :
    - développement
    - exécutable PyInstaller
    """

    return (get_base_path() / relative).resolve()


# ==========================================================
# RESOURCE DIR
# ==========================================================

def resource_dir(directory: str | Path) -> Path:
    """
    Alias pratique pour obtenir un dossier d'assets.
    """

    return resource_path(directory)