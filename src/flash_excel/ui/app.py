"""PyWebView application entry point for flash-excel."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Must be set before webview is imported to take effect. pywebview's stdlib
# records are picked up by the ezplog bridge (hook_logger) and land in the
# same file as the application logs.
os.environ.setdefault("PYWEBVIEW_LOG", "WARNING")

import webview  # type: ignore[import-untyped]  # noqa: E402
from webview.dom import DOMEventHandler  # type: ignore[import-untyped]  # noqa: E402

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

    window = webview.create_window(
        title="Flash-Excel",
        url=(_WEB_DIR / "index.html").as_uri(),
        js_api=api,
        width=1280,
        height=800,
        min_size=(900, 600),
        background_color="#161a20",
    )

    # Bound to the body rather than the drop zone: pywebview resolves "body"
    # through document.body on every call, so the handler survives the Vue
    # re-render that replaces the zone once files are loaded. dragover must
    # preventDefault, or the browser navigates to the file instead of
    # emitting a drop.
    def _bind_drop() -> None:
        # ty: create_window is typed Window | None, and Event.__iadd__ only
        # declares a plain Callable, not the DOMEventHandler it also accepts.
        body = window.dom.body  # ty: ignore[unresolved-attribute]
        swallow = DOMEventHandler(lambda _event: None, prevent_default=True)
        body.events.dragover += swallow  # ty: ignore[unsupported-operator]
        body.events.drop += DOMEventHandler(  # ty: ignore[unsupported-operator]
            api.on_file_drop, prevent_default=True
        )

    window.events.loaded += _bind_drop  # ty: ignore[unresolved-attribute]

    webview.start(debug=debug, icon=str(_ICON))
