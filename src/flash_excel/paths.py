# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import os
import sys
from pathlib import Path


def _get_base_dir() -> Path:
    # En mode compilé PyInstaller, les fichiers sont extraits dans sys._MEIPASS
    # En mode développement, on remonte depuis src/flash_excel/ vers la racine
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    return Path(__file__).parent.parent.parent


def _get_user_data_dir() -> Path:
    # Données écrites à l'exécution : jamais dans le dossier d'install, qui est
    # remplacé à chaque mise à jour (et lu seul en install machine-wide).
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / ".local" / "share"
    return base / "flash-excel"


PROJECT_ROOT: Path = _get_base_dir()

USER_DATA_DIR: Path = _get_user_data_dir()
LOG_DIR: Path = USER_DATA_DIR / "logs"
LOG_FILE: Path = LOG_DIR / "flash-excel.log"

BIN_DIR: Path = PROJECT_ROOT / "bin"

PRESETS_DIR: Path = BIN_DIR / "presets"
ASSETS_DIR: Path = BIN_DIR / "assets"
THEMES_CONFIG: Path = BIN_DIR / "config" / "theme.config.yaml"
APP_CONFIG: Path = BIN_DIR / "config" / "app.config.yaml"

__all__ = [
    "PROJECT_ROOT",
    "USER_DATA_DIR",
    "LOG_DIR",
    "LOG_FILE",
    "BIN_DIR",
    "PRESETS_DIR",
    "ASSETS_DIR",
    "THEMES_CONFIG",
    "APP_CONFIG",
]
