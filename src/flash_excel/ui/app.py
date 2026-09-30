"""PyWebView application entry point for flash-excel."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Doit être positionné avant l'import de webview pour prendre effet. Les
# records stdlib de pywebview sont captés par le pont ezplog (hook_logger) et
# atterrissent dans le même fichier que les logs applicatifs.
os.environ.setdefault("PYWEBVIEW_LOG", "WARNING")

import webview  # type: ignore[import-untyped]  # noqa: E402

from flash_excel.config import consume_installer_locale
from flash_excel.logs import log, setup_logging
from flash_excel.migration import migrate_legacy_presets
from flash_excel.paths import BIN_DIR
from flash_excel.ui.api import FlashExcelAPI

_WEB_DIR = Path(__file__).parent / "web"
_ICON = BIN_DIR / "assets" / "images" / "logo.ico"


def run() -> None:
    """Launch the flash-excel desktop window via PyWebView."""
    debug = "--debug" in sys.argv
    setup_logging(debug=debug)
    log("INFO", "starting")
    migrate_legacy_presets()
    consume_installer_locale()
    api = FlashExcelAPI()

    webview.create_window(
        title="Flash-Excel",
        url=(_WEB_DIR / "index.html").as_uri(),
        js_api=api,
        width=1280,
        height=800,
        min_size=(900, 600),
        background_color="#161a20",
    )

    webview.start(debug=debug, icon=str(_ICON))
