# ///////////////////////////////////////////////////////////////
# CONFIG - App configuration and theme loading
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import contextlib
import hashlib
import shutil

import yaml

from flash_excel.logs import log
from flash_excel.paths import (
    APP_CONFIG,
    APP_CONFIG_TEMPLATE,
    BUNDLED_THEMES_CONFIG,
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

# Repli minimal si le template du package est introuvable (bundle incomplet) :
# l'application doit démarrer avec une config valide, quitte à perdre les
# commentaires explicatifs.
_FALLBACK_TEMPLATE = (
    "appearance:\n  palette: {palette}\n  mode: {mode}\nlocale: {locale}\n"
)


def _template() -> str:
    """Retourne le gabarit d'app.config.yaml livré avec le package."""
    try:
        return APP_CONFIG_TEMPLATE.read_text(encoding="utf-8")
    except OSError:
        log("WARNING", f"template introuvable: {APP_CONFIG_TEMPLATE}, repli minimal")
        return _FALLBACK_TEMPLATE


def _resolve_palette(name: str) -> str:
    """Retourne ``name`` si la palette existe, sinon la palette par défaut.

    La config d'apparence est itinérante : elle peut désigner une palette que
    le catalogue du poste courant ne connaît pas (copie plus ancienne, palette
    ajoutée à la main sur un autre poste). Sans ce garde-fou le front ne trouve
    aucun token et retombe silencieusement sur le CSS par défaut, sans que rien
    ne dise pourquoi.
    """
    palettes = load_themes()
    if not palettes or name in palettes:
        return name
    log("WARNING", f"palette {name!r} absente du catalogue, retour au défaut")
    return _DEFAULTS["appearance"]["palette"]


def load_app_config() -> dict:
    """Charge la config, crée le fichier avec les défauts s'il n'existe pas."""
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
    """Persiste les réglages d'apparence et la locale en conservant les commentaires."""
    _write(palette, mode, locale)


def ensure_theme_config() -> None:
    """Amorce la copie utilisateur du catalogue de palettes, et la rafraîchit.

    Le catalogue vit dans %APPDATA% pour voyager avec app.config.yaml : un
    réglage itinérant ne peut pas désigner une palette absente du poste.
    Mais il est livré avec la version, donc une release qui ajoute une palette
    ou corrige un token doit atteindre l'utilisateur : on compare l'empreinte
    du catalogue embarqué à celle mémorisée lors du dernier amorçage, et on
    remplace la copie quand elle a changé — en conservant l'ancienne en .bak
    pour ne rien détruire chez qui l'aurait éditée.
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
                f"themes: catalogue mis à jour, ancienne copie en {THEMES_CONFIG.name}.bak",
            )
        else:
            log("INFO", f"themes: catalogue amorcé dans {THEMES_CONFIG}")
        THEMES_CONFIG.write_bytes(shipped)
        THEMES_STAMP.write_text(digest, encoding="utf-8")


def load_themes() -> dict:
    """Retourne le dict complet des palettes depuis theme.config.yaml."""
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
