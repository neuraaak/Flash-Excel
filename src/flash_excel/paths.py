# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Emplacements de fichiers de l'application.

Trois familles, délibérément séparées :

- le **dossier d'installation** (``BIN_DIR``) : lecture seule. Il est
  intégralement remplacé par robocopy à chaque auto-update tufup, donc rien
  d'écrit par l'utilisateur ne peut y survivre ;
- les **templates de config** (``CONFIG_TEMPLATES_DIR``) : données du package,
  livrées avec le code qui les consomme et matérialisées dans le profil
  utilisateur au premier démarrage ;
- les **configs utilisateur** (``APP_CONFIG``, ``THEMES_CONFIG``) dans
  ``%APPDATA%`` (Roaming) : elles voyagent ensemble d'un poste à l'autre, ce
  qui évite qu'un réglage itinérant désigne une palette absente en local ;
- les **logs** (``LOG_DIR``) dans ``%LOCALAPPDATA%`` : volumineux et liés à
  la machine, ils n'ont rien à faire dans un profil itinérant ;
- les **presets** (``PRESETS_DIR``) dans ``Documents\\flash-excel`` : ce sont
  des documents utilisateur, faits pour être ouverts, sauvegardés et échangés
  entre postes. Ils survivent volontairement à une désinstallation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_APP_FOLDER_NAME = "flash-excel"

# Clé de registre donnant le vrai chemin de « Documents ». Indispensable :
# OneDrive redirige couramment le dossier vers %USERPROFILE%\OneDrive\Documents,
# auquel cas ~/Documents pointe sur un dossier différent, voire inexistant.
_USER_SHELL_FOLDERS = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
)
_DOCUMENTS_VALUE = "Personal"

# ///////////////////////////////////////////////////////////////
# RESOLVERS
# ///////////////////////////////////////////////////////////////


def _get_base_dir() -> Path:
    # En mode compilé PyInstaller, les fichiers sont extraits dans sys._MEIPASS
    # En mode développement, on remonte depuis src/flash_excel/ vers la racine
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    return Path(__file__).parent.parent.parent


def _get_roaming_dir() -> Path:
    """Dossier des réglages utilisateur (%APPDATA%, repli POSIX)."""
    app_data = os.environ.get("APPDATA")
    base = Path(app_data) if app_data else Path.home() / ".config"
    return base / _APP_FOLDER_NAME


def _get_local_dir() -> Path:
    """Dossier des données locales à la machine (%LOCALAPPDATA%, repli POSIX)."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / ".local" / "share"
    return base / _APP_FOLDER_NAME


def _get_documents_dir() -> Path:
    """Dossier « Documents » de l'utilisateur, redirection OneDrive comprise.

    Le registre fait autorité : il reflète la redirection éventuelle, que
    ``~/Documents`` ignore. En cas d'échec (clé absente, plateforme non
    Windows), on retombe sur le chemin conventionnel.
    """
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _USER_SHELL_FOLDERS) as key:
                raw, _ = winreg.QueryValueEx(key, _DOCUMENTS_VALUE)
            resolved = os.path.expandvars(raw)
            if resolved:
                return Path(resolved)
        except OSError:
            pass
    return Path.home() / "Documents"


# ///////////////////////////////////////////////////////////////
# PATHS
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT: Path = _get_base_dir()

BIN_DIR: Path = PROJECT_ROOT / "bin"

# Données du package : résolues depuis le module, comme ui/web/, et non depuis
# PROJECT_ROOT — c'est PyInstaller (collect-data) qui les embarque.
PACKAGE_DIR: Path = Path(__file__).parent
CONFIG_TEMPLATES_DIR: Path = PACKAGE_DIR / "assets" / "config"

# Templates livrés avec la version : sources d'amorçage des configs
# utilisateur, et référence de fraîcheur pour le catalogue de palettes.
APP_CONFIG_TEMPLATE: Path = CONFIG_TEMPLATES_DIR / "app.config.yaml"
BUNDLED_THEMES_CONFIG: Path = CONFIG_TEMPLATES_DIR / "theme.config.yaml"

USER_CONFIG_DIR: Path = _get_roaming_dir()
APP_CONFIG: Path = USER_CONFIG_DIR / "app.config.yaml"
THEMES_CONFIG: Path = USER_CONFIG_DIR / "theme.config.yaml"
# Empreinte du catalogue livré au moment de l'amorçage, pour détecter qu'une
# nouvelle version en apporte un plus récent.
THEMES_STAMP: Path = USER_CONFIG_DIR / ".theme.source"

USER_DATA_DIR: Path = _get_local_dir()
LOG_DIR: Path = USER_DATA_DIR / "logs"
LOG_FILE: Path = LOG_DIR / "flash-excel.log"

USER_DOCUMENTS_DIR: Path = _get_documents_dir() / _APP_FOLDER_NAME
PRESETS_DIR: Path = USER_DOCUMENTS_DIR / "presets"

# Emplacements d'avant la sortie des données du dossier d'installation,
# lus une seule fois par la migration au démarrage (cf. flash_excel.migration).
LEGACY_APP_CONFIG: Path = BIN_DIR / "config" / "app.config.yaml"
LEGACY_PRESETS_DIR: Path = BIN_DIR / "presets"

__all__ = [
    "APP_CONFIG",
    "APP_CONFIG_TEMPLATE",
    "BIN_DIR",
    "BUNDLED_THEMES_CONFIG",
    "CONFIG_TEMPLATES_DIR",
    "LEGACY_APP_CONFIG",
    "LEGACY_PRESETS_DIR",
    "LOG_DIR",
    "LOG_FILE",
    "PRESETS_DIR",
    "PACKAGE_DIR",
    "PROJECT_ROOT",
    "THEMES_CONFIG",
    "THEMES_STAMP",
    "USER_CONFIG_DIR",
    "USER_DATA_DIR",
    "USER_DOCUMENTS_DIR",
]
