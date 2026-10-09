# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""File locations used by the application.

Three deliberately separate families:

- the **installation directory** (``BIN_DIR``): read-only. It is wholly
  replaced by robocopy on every tufup auto-update, so nothing the user writes
  can survive there;
- the **config templates** (``CONFIG_TEMPLATES_DIR``): package data, shipped
  with the code that consumes them and materialised into the user profile on
  first start;
- the **user configs** (``APP_CONFIG``, ``THEMES_CONFIG``) in ``%APPDATA%``
  (Roaming): they travel together from one machine to the next, which keeps a
  roaming setting from naming a palette that is missing locally;
- the **logs** (``LOG_DIR``) in ``%LOCALAPPDATA%``: bulky and tied to the
  machine, they have no business in a roaming profile;
- the **presets** (``PRESETS_DIR``) in ``Documents\\flash-excel``: these are
  user documents, meant to be opened, backed up and exchanged between
  machines. They deliberately survive an uninstall.
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

# Registry key holding the real path of "Documents". Required: OneDrive
# commonly redirects the folder to %USERPROFILE%\OneDrive\Documents, in which
# case ~/Documents points at a different folder, or at none at all.
_USER_SHELL_FOLDERS = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
)
_DOCUMENTS_VALUE = "Personal"

# ///////////////////////////////////////////////////////////////
# RESOLVERS
# ///////////////////////////////////////////////////////////////


def _get_base_dir() -> Path:
    # Under a PyInstaller build, files are extracted into sys._MEIPASS
    # In development, walk up from src/flash_excel/ to the project root
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    return Path(__file__).parent.parent.parent


def _get_roaming_dir() -> Path:
    """User settings directory (%APPDATA%, with a POSIX fallback)."""
    app_data = os.environ.get("APPDATA")
    base = Path(app_data) if app_data else Path.home() / ".config"
    return base / _APP_FOLDER_NAME


def _get_local_dir() -> Path:
    """Machine-local data directory (%LOCALAPPDATA%, with a POSIX fallback)."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / ".local" / "share"
    return base / _APP_FOLDER_NAME


def _get_documents_dir() -> Path:
    """The user's "Documents" folder, OneDrive redirection included.

    The registry is authoritative: it reflects any redirection, which
    ``~/Documents`` ignores. On failure (missing key, non-Windows platform),
    fall back to the conventional path.
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

# Package data: resolved from the module, like ui/web/, and not from
# PROJECT_ROOT — PyInstaller bundles them via collect-data.
PACKAGE_DIR: Path = Path(__file__).parent
CONFIG_TEMPLATES_DIR: Path = PACKAGE_DIR / "assets" / "config"

# Templates shipped with the release: the seed for the user configs, and the
# freshness reference for the palette catalogue.
APP_CONFIG_TEMPLATE: Path = CONFIG_TEMPLATES_DIR / "app.config.yaml"
BUNDLED_THEMES_CONFIG: Path = CONFIG_TEMPLATES_DIR / "theme.config.yaml"

USER_CONFIG_DIR: Path = _get_roaming_dir()
APP_CONFIG: Path = USER_CONFIG_DIR / "app.config.yaml"
THEMES_CONFIG: Path = USER_CONFIG_DIR / "theme.config.yaml"
# Fingerprint of the catalogue shipped at seeding time, used to detect that a
# new release brings a more recent one.
THEMES_STAMP: Path = USER_CONFIG_DIR / ".theme.source"
# Written by the Inno Setup installer ([INI]) with the language picked in the
# wizard. Read exactly once, when the user config is created.
INSTALLER_MARKER: Path = USER_CONFIG_DIR / "installer.ini"

USER_DATA_DIR: Path = _get_local_dir()
LOG_DIR: Path = USER_DATA_DIR / "logs"
LOG_FILE: Path = LOG_DIR / "flash-excel.log"

USER_DOCUMENTS_DIR: Path = _get_documents_dir() / _APP_FOLDER_NAME
PRESETS_DIR: Path = USER_DOCUMENTS_DIR / "presets"

# Locations used before user data moved out of the installation directory,
# read once by the startup migration (see flash_excel.migration).
LEGACY_APP_CONFIG: Path = BIN_DIR / "config" / "app.config.yaml"
LEGACY_PRESETS_DIR: Path = BIN_DIR / "presets"

__all__ = [
    "APP_CONFIG",
    "APP_CONFIG_TEMPLATE",
    "BIN_DIR",
    "BUNDLED_THEMES_CONFIG",
    "CONFIG_TEMPLATES_DIR",
    "INSTALLER_MARKER",
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
