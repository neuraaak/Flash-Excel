# ///////////////////////////////////////////////////////////////
# CONFIG - App configuration and theme loading
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import configparser
import contextlib
import hashlib
import shutil
import sys

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
    "csv": {
        "separator": "auto",
        "decimal": "auto",
    },
}

# Regional settings Excel itself reads to decide how a CSV is parsed and
# written. Aligning on them is what makes a produced file open in columns on a
# double-click instead of as one text blob.
_INTERNATIONAL_KEY = r"Control Panel\International"
_LIST_SEPARATOR_VALUE = "sList"
_DECIMAL_SEPARATOR_VALUE = "sDecimal"

# Stored as tokens rather than the characters themselves: a raw tab or a comma
# in YAML needs quoting, and the template is filled with str.format().
_SEPARATOR_TOKENS: dict[str, str] = {
    "semicolon": ";",
    "comma": ",",
    "tab": "	",
}
_DECIMAL_TOKENS = frozenset({"auto", "comma", "dot"})

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
                current["csv"]["separator"],
                current["csv"]["decimal"],
            )
            log("INFO", f"locale taken from the installer: {locale}")

    with contextlib.suppress(OSError):
        INSTALLER_MARKER.unlink()
    return locale


def _regional(value_name: str, fallback: str) -> str:
    """Read one value from the Windows regional settings, or return a fallback."""
    if sys.platform != "win32":
        return fallback
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _INTERNATIONAL_KEY) as key:
            raw, _ = winreg.QueryValueEx(key, value_name)
    except OSError:
        log("WARNING", f"regional setting {value_name} unreadable, using {fallback!r}")
        return fallback
    return str(raw) or fallback


def resolve_csv_output(csv_config: dict | None = None) -> tuple[str, bool]:
    """Return the ``(separator, decimal_comma)`` pair a CSV write should use.

    Both settings default to ``"auto"``, which means: take what the machine's
    regional settings say, because that is exactly what Excel will assume when
    it opens the file. An explicit token overrides it, for a downstream
    consumer that wants a fixed format whatever the machine.

    Args:
        csv_config: The ``csv`` section of the app config. ``None`` or a
            missing key falls back to ``"auto"``.

    Returns:
        tuple[str, bool]: Delimiter character, and whether decimal numbers are
            written with a comma.
    """
    config = csv_config or {}

    separator = config.get("separator", "auto")
    resolved_sep = _SEPARATOR_TOKENS.get(
        separator, _regional(_LIST_SEPARATOR_VALUE, ";")
    )

    decimal = config.get("decimal", "auto")
    if decimal in {"comma", "dot"}:
        decimal_comma = decimal == "comma"
    else:
        decimal_comma = _regional(_DECIMAL_SEPARATOR_VALUE, ",") == ","

    # A comma delimiter and a comma decimal mark cannot coexist: every float
    # would split its own cell. The delimiter wins; the user asked for it.
    if resolved_sep == "," and decimal_comma:
        decimal_comma = False

    return resolved_sep, decimal_comma


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


def _defaults() -> dict:
    """Return a fresh, mutable copy of the default config."""
    return {
        "appearance": dict(_DEFAULTS["appearance"]),
        "locale": _DEFAULTS["locale"],
        "csv": dict(_DEFAULTS["csv"]),
    }


def _valid(value: object, allowed: set[str] | frozenset[str]) -> str:
    """Return ``value`` when it is an allowed token, else ``"auto"``.

    The config is hand-editable, so an unknown token must degrade to the
    automatic behaviour rather than reach the writer as a delimiter.
    """
    return value if isinstance(value, str) and value in allowed else "auto"


def load_app_config() -> dict:
    """Load the config, creating the file with the defaults if it is absent."""
    if not APP_CONFIG.exists():
        defaults = _defaults()
        _write(
            defaults["appearance"]["palette"],
            defaults["appearance"]["mode"],
            defaults["locale"],
            defaults["csv"]["separator"],
            defaults["csv"]["decimal"],
        )
        return defaults
    try:
        raw = yaml.safe_load(APP_CONFIG.read_text(encoding="utf-8")) or {}
        app = raw.get("appearance", {})
        csv_section = raw.get("csv", {}) or {}
        return {
            "appearance": {
                "palette": _resolve_palette(
                    app.get("palette", _DEFAULTS["appearance"]["palette"])
                ),
                "mode": app.get("mode", _DEFAULTS["appearance"]["mode"]),
            },
            "locale": raw.get("locale", _DEFAULTS["locale"]),
            "csv": {
                "separator": _valid(
                    csv_section.get("separator"), set(_SEPARATOR_TOKENS) | {"auto"}
                ),
                "decimal": _valid(csv_section.get("decimal"), _DECIMAL_TOKENS),
            },
        }
    except Exception:
        return _defaults()


def save_app_config(
    palette: str,
    mode: str,
    locale: str = "en",
    csv_separator: str = "auto",
    csv_decimal: str = "auto",
) -> None:
    """Persist the appearance, locale and CSV settings, keeping the comments."""
    _write(
        palette,
        mode,
        locale,
        _valid(csv_separator, set(_SEPARATOR_TOKENS) | {"auto"}),
        _valid(csv_decimal, _DECIMAL_TOKENS),
    )


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


def _write(
    palette: str, mode: str, locale: str, csv_separator: str, csv_decimal: str
) -> None:
    APP_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    APP_CONFIG.write_text(
        _template().format(
            palette=palette,
            mode=mode,
            locale=locale,
            csv_separator=csv_separator,
            csv_decimal=csv_decimal,
        ),
        encoding="utf-8",
    )
