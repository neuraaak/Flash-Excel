# ///////////////////////////////////////////////////////////////
# CONFIG - App configuration and theme loading
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import configparser
import contextlib
import hashlib
import shutil

import yaml

from flash_excel.logs import log
from flash_excel.paths import (
    APP_CONFIG,
    APP_CONFIG_TEMPLATE,
    BUNDLED_THEMES_CONFIG,
    INSTALLER_MARKER,
    THEMES_CONFIG,
    THEMES_STAMP,
)

_DEFAULTS: dict = {
    "appearance": {
        "palette": "blue-gray",
        "mode": "dark",
    },
    "locale": "en",
}

# Languages offered by the Inno Setup wizard ([tool.ezcompiler.installer]
# languages) mapped to the application locales. Any other value falls back to
# the default: the wizard may gain a language before the UI translates it.
_INNO_LOCALES: dict[str, str] = {
    "french": "fr",
    "english": "en",
}

# Minimal fallback when the package template is missing (incomplete bundle):
# the application must start with a valid config, even at the cost of losing
# the explanatory comments.
_FALLBACK_TEMPLATE = (
    "appearance:\n  palette: {palette}\n  mode: {mode}\nlocale: {locale}\n"
)


def _template() -> str:
    """Return the app.config.yaml template shipped with the package."""
    try:
        return APP_CONFIG_TEMPLATE.read_text(encoding="utf-8")
    except OSError:
        log("WARNING", f"template not found: {APP_CONFIG_TEMPLATE}, minimal fallback")
        return _FALLBACK_TEMPLATE


def _installer_locale() -> str | None:
    """Return the locale derived from the language picked in the installer.

    Returns:
        str | None: Application locale, or None if the marker is unreadable
            or carries a language the application does not know.
    """
    try:
        parser = configparser.ConfigParser()
        parser.read(INSTALLER_MARKER, encoding="utf-8-sig")
        language = parser.get("Setup", "Language", fallback="").strip().lower()
    except (OSError, configparser.Error):
        log("WARNING", f"unreadable installer marker: {INSTALLER_MARKER}")
        return None

    locale = _INNO_LOCALES.get(language)
    if locale is None and language:
        log("WARNING", f"unknown installer language: {language!r}")
    return locale


def consume_installer_locale() -> str | None:
    """Apply the language picked in the installer, then clear the marker.

    The Inno Setup installer writes ``installer.ini`` into %APPDATA% on every
    install. It is a single-use message, not a state: apply it — creating the
    config when needed, otherwise touching only its locale — then delete it.
    A reinstall therefore does impose the language asked for in the wizard,
    while changes made afterwards in the application stick, there being no
    marker left to overwrite them.

    The marker is deleted even when it is unusable: keeping it would replay
    the same failure on every start.

    Returns:
        str | None: The locale applied, or None if nothing was done.
    """
    if not INSTALLER_MARKER.is_file():
        return None

    locale = _installer_locale()
    if locale is not None:
        current = load_app_config()
        if current["locale"] != locale:
            save_app_config(
                current["appearance"]["palette"],
                current["appearance"]["mode"],
                locale,
            )
            log("INFO", f"locale taken from the installer: {locale}")

    with contextlib.suppress(OSError):
        INSTALLER_MARKER.unlink()
    return locale


def _resolve_palette(name: str) -> str:
    """Return ``name`` if the palette exists, else the default palette.

    The appearance config roams: it may name a palette the current machine's
    catalogue does not know (an older copy, a palette added by hand on another
    machine). Without this guard the front-end finds no token and silently
    falls back to the default CSS, with nothing saying why.
    """
    palettes = load_themes()
    if not palettes or name in palettes:
        return name
    log("WARNING", f"palette {name!r} missing from the catalogue, using the default")
    return _DEFAULTS["appearance"]["palette"]


def load_app_config() -> dict:
    """Load the config, creating the file with the defaults if it is absent."""
    if not APP_CONFIG.exists():
        _write(
            _DEFAULTS["appearance"]["palette"],
            _DEFAULTS["appearance"]["mode"],
            _DEFAULTS["locale"],
        )
        return {
            "appearance": dict(_DEFAULTS["appearance"]),
            "locale": _DEFAULTS["locale"],
        }
    try:
        raw = yaml.safe_load(APP_CONFIG.read_text(encoding="utf-8")) or {}
        app = raw.get("appearance", {})
        return {
            "appearance": {
                "palette": _resolve_palette(
                    app.get("palette", _DEFAULTS["appearance"]["palette"])
                ),
                "mode": app.get("mode", _DEFAULTS["appearance"]["mode"]),
            },
            "locale": raw.get("locale", _DEFAULTS["locale"]),
        }
    except Exception:
        return {
            "appearance": dict(_DEFAULTS["appearance"]),
            "locale": _DEFAULTS["locale"],
        }


def save_app_config(palette: str, mode: str, locale: str = "en") -> None:
    """Persist the appearance settings and locale, keeping the comments."""
    _write(palette, mode, locale)


def ensure_theme_config() -> None:
    """Seed the user copy of the palette catalogue, and refresh it.

    The catalogue lives in %APPDATA% so that it travels with app.config.yaml:
    a roaming setting cannot name a palette the machine lacks. It is shipped
    with the release though, so a version that adds a palette or fixes a token
    must reach the user: compare the fingerprint of the bundled catalogue with
    the one recorded at the last seeding, and replace the copy when it has
    changed — keeping the previous one as .bak so nothing is destroyed for
    anyone who edited it.
    """
    if not BUNDLED_THEMES_CONFIG.is_file():
        return

    with contextlib.suppress(OSError):
        shipped = BUNDLED_THEMES_CONFIG.read_bytes()
        digest = hashlib.sha256(shipped).hexdigest()
        stamped = (
            THEMES_STAMP.read_text(encoding="utf-8").strip()
            if THEMES_STAMP.is_file()
            else ""
        )

        if THEMES_CONFIG.is_file() and stamped == digest:
            return

        THEMES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        if THEMES_CONFIG.is_file():
            shutil.copy2(THEMES_CONFIG, THEMES_CONFIG.with_suffix(".yaml.bak"))
            log(
                "INFO",
                f"themes: catalogue updated, previous copy at {THEMES_CONFIG.name}.bak",
            )
        else:
            log("INFO", f"themes: catalogue seeded at {THEMES_CONFIG}")
        THEMES_CONFIG.write_bytes(shipped)
        THEMES_STAMP.write_text(digest, encoding="utf-8")


def load_themes() -> dict:
    """Return the full palette dict from theme.config.yaml."""
    ensure_theme_config()
    try:
        data = yaml.safe_load(THEMES_CONFIG.read_text(encoding="utf-8")) or {}
        return data.get("palette", {})
    except Exception:
        return {}


def _write(palette: str, mode: str, locale: str) -> None:
    APP_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    APP_CONFIG.write_text(
        _template().format(palette=palette, mode=mode, locale=locale),
        encoding="utf-8",
    )
