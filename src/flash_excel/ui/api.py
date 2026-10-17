"""Python API exposed to JS via webview.expose(api).

Every public method becomes ``await pywebview.api.<method>()`` in JS.
Methods must be synchronous from Python's perspective; pywebview wraps
them in promises on the JS side automatically.

Return convention: always return a dict with:
  {"ok": true, "data": <payload>}       on success
  {"ok": false, "error": "<message>"}   on failure
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any

import webview  # type: ignore[import-untyped]
from pydantic import TypeAdapter
from webview import FileDialog  # type: ignore[import-untyped]  # noqa: F401

from flash_excel._version import __version__
from flash_excel.config import (
    load_app_config,
    load_themes,
    resolve_csv_output,
    save_app_config,
)
from flash_excel.core.models import Preset, PresetMeta, Step
from flash_excel.io.loader import detect_separator, read_schema
from flash_excel.io.models import FileLoaderResult
from flash_excel.logs import log
from flash_excel.paths import DEFAULT_OUTPUT_DIR, PRESETS_DIR
from flash_excel.presets import delete_preset, list_presets, load_preset, save_preset

_step_adapter: TypeAdapter[Step] = TypeAdapter(Step)

_NO_ACTIVE_WINDOW = "No active window"

# Actions the UI edits as one multi-row table but the preset stores as one step
# per row. Per action: the item keys kept when aggregating, and the keys that
# must be truthy for a row to be worth expanding back into a step.
_AGGREGATED_ACTIONS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "add_computed_column": (("target", "expression"), ("target", "expression")),
    "clean_text": (("columns", "ops", "case"), ("columns",)),
    "replace_values": (("column", "mapping"), ("column", "mapping")),
}


def _expand_items(steps_payload: list) -> list[dict]:
    """Flatten the UI's items[] payloads into one raw step dict per row."""
    expanded: list[dict] = []
    for raw in steps_payload:
        if not raw:
            continue
        action = raw.get("action")
        required = _AGGREGATED_ACTIONS.get(action, (None, None))[1]
        if required is None or "items" not in raw:
            expanded.append(raw)
            continue
        expanded.extend(
            {"action": action, **item}
            for item in raw["items"]
            if all(item.get(key) for key in required)
        )
    return expanded


def _ok(data: Any = None) -> dict:
    return {"ok": True, "data": data}


def _err(message: str) -> dict:
    return {"ok": False, "error": message}


class FlashExcelAPI:
    """Stateful API instance — one per application lifetime."""

    def __init__(self) -> None:
        self._loaded_file: FileLoaderResult | None = None
        self._source_columns: list[str] = []
        self._source_schema: dict[str, str] = {}
        self._source_file: str = ""
        self._source_file_path: str = ""
        self._current_preset_path: Path | None = None
        self._step_payloads: dict[str, dict] = {}
        self._run_thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()

    # ------------------------------------------------------------------
    # Debug bridge (JS → Python)
    # ------------------------------------------------------------------

    def debug_log(self, msg: str) -> dict:
        """Relay a JS debug message to the Python console/log."""
        log("INFO", f"[js] {msg}")
        return _ok()

    # ------------------------------------------------------------------
    # Application version & auto-update (tufup)
    # ------------------------------------------------------------------

    def get_version(self) -> dict:
        """Return the running application version."""
        return _ok({"version": __version__})

    def check_update(self) -> dict:
        """Check the TUF repository for a newer version.

        Returns ``{"available": bool, "version": str | None, "error": str | None}``.
        Auto-update only works from the packaged app (the tufup client files are
        bundled at build time), so in dev (non-frozen) this always reports no
        update. A failed check (offline, signature error, non-writable cache) is
        logged with a full traceback to the application log and surfaced via
        the ``error`` field, but never raises.
        """
        if not getattr(sys, "frozen", False):
            return _ok({"available": False, "version": None, "error": None})
        try:
            import update  # ty: ignore[unresolved-import]  # generated at build time, bundled at the archive root

            latest = update.get_latest_version()
            log("INFO", f"update check ok: current={__version__} latest={latest!r}")
            return _ok(
                {"available": latest is not None, "version": latest, "error": None}
            )
        except Exception as exc:  # noqa: BLE001 - a failed check is not fatal
            log("ERROR", f"update check FAILED: {exc!r}\n{traceback.format_exc()}")
            return _ok({"available": False, "version": None, "error": str(exc)})

    def apply_update(self) -> dict:
        """Download and apply the available update via tufup, then quit.

        tufup's Windows installer launches a robocopy script (non-blocking) and
        then calls ``sys.exit(0)`` from *this* pywebview worker thread. That
        raises ``SystemExit`` (which is NOT an ``Exception``) and only kills the
        worker thread, leaving the process alive — so robocopy loops forever on
        ERROR 32 because the running .exe/.pyd files are still locked. We catch
        that ``SystemExit`` as the "installer launched" signal and force-quit
        with ``os._exit(0)`` to release the locks. Returns ``{"applied": bool}``.
        """
        if not getattr(sys, "frozen", False):
            return _err("Auto-update is only available in the packaged application")

        def _force_quit() -> None:
            # Let the response make it back to the JS side, close the window,
            # then kill the process outright to release the locked files that
            # tufup's robocopy script has to replace.
            time.sleep(0.3)
            for window in webview.windows:
                with contextlib.suppress(Exception):
                    window.destroy()
            os._exit(0)

        try:
            import update  # ty: ignore[unresolved-import]  # generated at build time, bundled at the archive root

            # A normal return means no update was applied (already current).
            # An actual update never comes back here: tufup raises SystemExit
            # once it has launched its install script.
            applied = update.check_and_apply(skip_confirmation=True)
            log("INFO", f"update apply: no-op (applied={applied})")
            return _ok({"applied": bool(applied)})
        except SystemExit:  # NOSONAR - see docstring: not reraised on purpose
            log("INFO", "update apply: installer launched (SystemExit) -> force quit")
            threading.Thread(target=_force_quit, daemon=True).start()
            return _ok({"applied": True})
        except Exception as exc:
            log("ERROR", f"update apply FAILED: {exc!r}\n{traceback.format_exc()}")
            return _err(str(exc))

    # ------------------------------------------------------------------
    # Settings & themes
    # ------------------------------------------------------------------

    def get_app_config(self) -> dict:
        """Return the current app configuration (appearance, etc.)."""
        try:
            return _ok(load_app_config())
        except Exception as exc:
            return _err(str(exc))

    def save_app_config(
        self,
        palette: str,
        mode: str,
        locale: str = "en",
        csv_separator: str = "auto",
        csv_decimal: str = "auto",
    ) -> dict:
        """Persist appearance, locale and CSV settings to app.config.yaml."""
        try:
            save_app_config(palette, mode, locale, csv_separator, csv_decimal)
            return _ok()
        except Exception as exc:
            return _err(str(exc))

    def get_themes(self) -> dict:
        """Return all palette definitions from theme.config.yaml."""
        try:
            return _ok(load_themes())
        except Exception as exc:
            return _err(str(exc))

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    def get_presets(self) -> dict:
        """Return list of preset metadata dicts.

        A preset that cannot be read is still listed, carrying an ``error``
        field instead of its metadata: dropping it would make a corrupt file
        look like a deleted one.
        """
        try:
            paths = list_presets(PRESETS_DIR)
            result = []
            for p in paths:
                try:
                    preset = load_preset(p)
                except Exception as exc:
                    log("ERROR", f"unreadable preset {p.name}: {exc}")
                    result.append(
                        {
                            "name": p.stem,
                            "description": "",
                            "step_count": 0,
                            "path": str(p),
                            "error": str(exc),
                        }
                    )
                    continue
                result.append(
                    {
                        "name": preset.meta.name,
                        "description": preset.meta.description or "",
                        "step_count": len(preset.steps),
                        "path": str(p),
                    }
                )
            return _ok(result)
        except Exception as exc:
            return _err(str(exc))

    def load_preset(self, preset_path: str) -> dict:
        """Load a preset by absolute path and return its full data."""
        try:
            path = Path(preset_path)
            preset = load_preset(path)
            self._current_preset_path = path
            self._step_payloads = {}
            # Restore cached source info from preset meta so re-saves
            # without a loaded file keep the original column/schema data.
            if preset.meta.source_columns:
                self._source_columns = list(preset.meta.source_columns)
            if preset.meta.source_types:
                self._source_schema = dict(preset.meta.source_types)
            if preset.meta.source_file:
                self._source_file = preset.meta.source_file
            for step in preset.steps:
                step_dict = step.model_dump()
                action = step_dict.pop("action")
                self._step_payloads[action] = {"action": action, **step_dict}
            return _ok(self._preset_to_dict(preset))
        except Exception as exc:
            return _err(str(exc))

    def new_preset(self, name: str) -> dict:
        """Create a fresh empty preset in memory and return its data."""
        try:
            name = name.strip()
            if not name:
                return _err("Preset name cannot be empty")
            preset = Preset(meta=PresetMeta(name=name), steps=[])
            path = PRESETS_DIR / f"{self._name_to_filename(name)}.toml"
            self._current_preset_path = path
            self._step_payloads = {}
            return _ok(self._preset_to_dict(preset))
        except Exception as exc:
            return _err(str(exc))

    @staticmethod
    def _name_to_filename(name: str) -> str:
        """Convert a preset display name to a snake_case filename stem."""
        import re

        slug = name.strip().lower()
        slug = re.sub(r"[^\w\s]", "", slug)  # strip punctuation
        slug = re.sub(r"\s+", "_", slug)  # spaces → underscore
        slug = re.sub(r"_+", "_", slug).strip("_")
        return slug or "preset"

    def save_preset(self, name: str, steps_payload: list) -> dict:
        """Persist current preset to disk.

        Returns ``{"path": str, "rejected": [...]}``. ``rejected`` lists the
        payloads that failed validation and are therefore *not* in the saved
        file, so the UI can say so instead of losing them silently.
        """
        try:
            name = name.strip()
            new_path = PRESETS_DIR / f"{self._name_to_filename(name)}.toml"
            old_path = self._current_preset_path
            renaming = old_path is not None and old_path != new_path

            # Two presets whose names differ only by punctuation share a
            # filename; overwriting the other one would destroy it.
            if renaming and new_path.exists():
                return _err(
                    f"A preset already uses the file '{new_path.name}'. "
                    "Choose another name."
                )

            steps: list[Step] = []
            rejected: list[dict] = []
            for raw in _expand_items(steps_payload):
                try:
                    steps.append(_step_adapter.validate_python(raw))
                except Exception as exc:
                    log("WARNING", f"step rejected on save: {raw.get('action')}: {exc}")
                    rejected.append(
                        {"action": raw.get("action", "?"), "reason": str(exc)}
                    )

            preset = Preset(
                meta=PresetMeta(
                    name=name,
                    source_columns=self._source_columns,
                    source_types=self._source_schema,
                    source_file=self._source_file,
                ),
                steps=steps,
            )
            # Write before unlinking the previous file: a failed write must not
            # leave the user with neither copy.
            save_preset(preset, new_path)
            if renaming and old_path is not None and old_path.exists():
                old_path.unlink()
            self._current_preset_path = new_path
            return _ok({"path": str(new_path), "rejected": rejected})
        except Exception as exc:
            return _err(str(exc))

    def delete_preset(self, preset_path: str) -> dict:
        """Delete a preset file."""
        try:
            path = Path(preset_path)
            delete_preset(path)
            if self._current_preset_path == path:
                self._current_preset_path = None
                self._step_payloads = {}
            return _ok()
        except Exception as exc:
            return _err(str(exc))

    def export_preset(self, preset_path: str) -> dict:
        """Open a save dialog and copy the preset TOML to the chosen location."""
        try:
            src = Path(preset_path)
            try:
                src.resolve().relative_to(PRESETS_DIR.resolve())
            except ValueError:
                return _err("Preset file is outside the presets directory")
            if src.suffix.lower() != ".toml":
                return _err("Preset file must be a TOML file")
            if not src.exists():
                return _err("Preset file not found")
            window = webview.active_window()
            if window is None:
                return _err(_NO_ACTIVE_WINDOW)
            result = window.create_file_dialog(  # type: ignore[union-attr]
                FileDialog.SAVE,
                directory=str(Path.home()),
                save_filename=src.name,
                file_types=("TOML files (*.toml)",),
            )
            if not result:
                return _ok({"cancelled": True})
            dest = Path(
                str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            )
            dest.write_bytes(src.read_bytes())
            return _ok({"dest": str(dest)})
        except Exception as exc:
            return _err(str(exc))

    # ------------------------------------------------------------------
    # File loading
    # ------------------------------------------------------------------

    def open_file_dialog(self) -> dict:
        """Open native file picker and load the selected file."""
        try:
            window = webview.active_window()
            if window is None:
                return _err(_NO_ACTIVE_WINDOW)
            result = window.create_file_dialog(  # type: ignore[union-attr]
                FileDialog.OPEN,
                allow_multiple=False,
                file_types=("Supported files (*.xlsx;*.xls;*.xlsm;*.csv)",),
            )
            if not result:
                return _ok({"cancelled": True})
            return self._load_file_path(result[0])
        except Exception as exc:
            return _err(str(exc))

    def open_folder_dialog(self) -> dict:
        """Open native folder picker and return the selected path."""
        try:
            window = webview.active_window()
            if window is None:
                return _err(_NO_ACTIVE_WINDOW)
            result = window.create_file_dialog(  # type: ignore[union-attr]
                FileDialog.FOLDER,
            )
            if not result:
                return _ok({"cancelled": True})
            folder = (
                str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            )
            return _ok({"folder": folder})
        except Exception as exc:
            return _err(str(exc))

    def clear_file(self) -> dict:
        """Unload the current file."""
        self._loaded_file = None
        self._source_columns = []
        self._source_schema = {}
        return _ok()

    # ------------------------------------------------------------------
    # Step payloads
    # ------------------------------------------------------------------

    def get_step_payload(self, action: str) -> dict:
        """Return the current in-memory payload for a given action."""
        return _ok(self._step_payloads.get(action, {}))

    def set_step_payload(self, action: str, payload: dict) -> dict:
        """Store an edited step payload in memory."""
        log("DEBUG", f"set_step_payload: action={action} payload={payload}")
        if payload:
            self._step_payloads[action] = payload
        else:
            self._step_payloads.pop(action, None)
        return _ok()

    def get_source_columns(self) -> dict:
        """Return the column list of the currently loaded file."""
        return _ok(self._source_columns)

    def get_default_output_folder(self) -> dict:
        """Return the absolute folder a run writes to by default."""
        return _ok({"folder": str(DEFAULT_OUTPUT_DIR)})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file_path(self, path_str: str) -> dict:
        try:
            path = Path(path_str)
            result = FileLoaderResult.from_path(path)
            self._loaded_file = result
            # No preset is selected yet at this point, so the separator can only
            # come from the file itself (ignored for Excel).
            self._source_schema = read_schema(path, detect_separator(path))
            self._source_columns = list(self._source_schema.keys())
            self._source_file = result.file_name
            self._source_file_path = str(path)
            return _ok(
                {
                    "path": str(path),
                    "file_name": result.file_name,
                    "size_bytes": result.size_bytes,
                    "file_type": result.file_type,
                    "columns": self._source_columns,
                    "schema": self._source_schema,
                }
            )
        except Exception as exc:
            return _err(str(exc))

    # ------------------------------------------------------------------
    # Run execution
    # ------------------------------------------------------------------

    def run_preset(
        self,
        preset_path: str,
        file_path: str,
        output_config: dict,
    ) -> dict:
        """Start pipeline execution in a background thread.

        Returns immediately. Progress is pushed via window.flashEvent().
        """
        if self._run_thread is not None and self._run_thread.is_alive():
            return _err("A run is already in progress")
        self._stop_event = threading.Event()
        self._run_thread = threading.Thread(
            target=self._run_worker,
            args=(preset_path, file_path, output_config),
            daemon=True,
        )
        self._run_thread.start()
        return _ok()

    def stop_run(self) -> dict:
        """Request the running pipeline to stop after the current step."""
        self._stop_event.set()
        return _ok()

    def _push(self, event_type: str, data: dict) -> None:
        """Push an event to the JS layer via evaluate_js."""
        js = f"window.flashEvent && window.flashEvent({json.dumps(event_type)}, {json.dumps(data)})"
        try:
            webview.windows[0].evaluate_js(js)
        except Exception as exc:
            log("ERROR", f"_push failed: {exc}")

    def _read_source(self, source: Path, preset: Preset):
        """Load the source file using the input settings saved by its preset."""
        from flash_excel.io.loader import detect_separator, read_csv, read_excel

        if source.suffix.lower() == ".csv":
            separator = preset.meta.csv_separator or detect_separator(source)
            return read_csv(
                source,
                separator,
                preset.meta.csv_encoding,
                preset.meta.csv_decimal_comma,
            )
        return read_excel(source)

    def _run_steps(self, df, preset: Preset, error_mode: str):
        """Apply preset steps and emit progress; return None when execution stops."""
        from flash_excel.core.registry import REGISTRY

        for idx, step in enumerate(preset.steps):
            if self._stop_event.is_set():
                self._push("log", {"level": "warn", "key": "log.run_stopped"})
                return None

            step_name = step.action
            rows_in = len(df)
            try:
                handler = REGISTRY.get(step_name)
                if handler is None:
                    raise KeyError(f"No handler for action '{step_name}'")
                df = handler(df, **step.model_dump(exclude={"action"}))
                self._push(
                    "step",
                    {
                        "step_index": idx,
                        "step_name": step_name,
                        "rows_in": rows_in,
                        "rows_out": len(df),
                    },
                )
            except Exception as exc:
                self._push(
                    "error",
                    {"step_index": idx, "step_name": step_name, "message": str(exc)},
                )
                if error_mode != "ignore":
                    if error_mode == "skip":
                        self._push(
                            "log",
                            {
                                "level": "warn",
                                "key": "log.skip_error",
                                "params": {"step": step_name},
                            },
                        )
                    return None
        return df

    def _run_worker(
        self,
        preset_path: str,
        file_path: str,
        output_config: dict,
    ) -> None:
        """Pipeline execution worker — runs in a background thread."""
        from flash_excel.io.writer import write_dataframe
        from flash_excel.presets import load_preset as _load_preset

        t_start = time.monotonic()
        error_mode = output_config.get("error_mode", "skip")

        try:
            src = Path(file_path)
            # The preset comes first: it carries the CSV separator and encoding
            # the read needs.
            preset = _load_preset(Path(preset_path))
            self._push(
                "log",
                {"level": "info", "key": "log.loading", "params": {"file": src.name}},
            )
            df = self._read_source(src, preset)
            self._push(
                "log",
                {
                    "level": "info",
                    "key": "log.parsed",
                    "params": {"rows": len(df), "cols": len(df.columns)},
                },
            )

            total = len(preset.steps)
            self._push(
                "log",
                {
                    "level": "info",
                    "key": "log.preset_steps",
                    "params": {"name": preset.meta.name, "count": total},
                },
            )

            df = self._run_steps(df, preset, error_mode)
            if df is None:
                return

            out_path, fmt = self._resolve_output_path(file_path, output_config)
            self._push(
                "log",
                {
                    "level": "info",
                    "key": "log.writing_output",
                    "params": {"path": out_path},
                },
            )
            app_config = load_app_config()
            separator, decimal_comma = resolve_csv_output(app_config.get("csv"))
            write_dataframe(
                df,
                Path(out_path),
                fmt,
                locale=app_config.get("locale", "en"),
                separator=separator,
                decimal_comma=decimal_comma,
            )

            elapsed = round(time.monotonic() - t_start, 2)
            self._push(
                "done",
                {
                    "elapsed_s": elapsed,
                    "rows_out": len(df),
                    "output_path": out_path,
                },
            )

        except Exception as exc:
            elapsed = round(time.monotonic() - t_start, 2)
            # fatal: nothing follows this, not even a "done". Without the flag
            # the UI stays on "running" forever under error_mode "ignore" —
            # which is where a source file locked by Excel lands.
            self._push(
                "error",
                {
                    "step_index": -1,
                    "step_name": "init",
                    "message": str(exc),
                    "fatal": True,
                },
            )
            self._push(
                "log",
                {
                    "level": "err",
                    "key": "log.run_failed",
                    "params": {"elapsed": elapsed, "error": str(exc)},
                },
            )

    @staticmethod
    def _preset_to_dict(preset: Preset) -> dict:
        # Aggregate multi-step actions (add_computed_column, clean_text,
        # replace_values) into single payloads with items[], keeping the
        # position of the first occurrence of each aggregated action.
        aggregated: dict[str, list[dict]] = {a: [] for a in _AGGREGATED_ACTIONS}
        first_pos: dict[str, int] = {}
        other_steps: list[dict | None] = []

        for s in preset.steps:
            d = s.model_dump()
            action = d["action"]
            keys = _AGGREGATED_ACTIONS.get(action, (None, None))[0]
            if keys is None:
                other_steps.append(d)
                continue
            if action not in first_pos:
                first_pos[action] = len(other_steps)
                other_steps.append(None)  # placeholder
            aggregated[action].append({k: d[k] for k in keys})

        # Fill placeholders with aggregated payloads.
        for action, items in aggregated.items():
            if items:
                other_steps[first_pos[action]] = {"action": action, "items": items}

        return {
            "name": preset.meta.name,
            "description": preset.meta.description or "",
            "source_columns": preset.meta.source_columns or [],
            "source_types": preset.meta.source_types or {},
            "source_file": preset.meta.source_file or "",
            "steps": [s for s in other_steps if s is not None],
        }

    @staticmethod
    def _resolve_output_path(
        file_path: str,
        output_config: dict,
    ) -> tuple[str, str]:
        """Compute the output file path from source path and output config.

        Args:
            file_path: Absolute path to the source file.
            output_config: Dict with keys ``'format'``, ``'folder'``, ``'pattern'``.
                ``'format'`` can be ``'keep'``, ``'xlsx'``, ``'csv'``, or ``'parquet'``.
                ``'pattern'`` may contain ``'{name}'`` placeholder (stem of source).

        Returns:
            tuple[str, str]: The output path, and the format it resolved to
                (never ``'keep'`` — ``write_dataframe`` needs a real format).
        """
        src = Path(file_path)
        stem = src.stem
        fmt = output_config.get("format", "keep")
        if fmt == "keep":
            fmt = src.suffix.lstrip(".") or "xlsx"
        pattern = output_config.get("pattern", "{name}_clean")
        base_name = pattern.replace("{name}", stem)
        # A relative folder would resolve against the working directory, which
        # for the installed app is the installation folder — replaced by every
        # auto-update. Anchor it to the user's Documents instead.
        folder = Path(output_config.get("folder") or DEFAULT_OUTPUT_DIR)
        if not folder.is_absolute():
            folder = DEFAULT_OUTPUT_DIR / folder
        return str(folder / f"{base_name}.{fmt}"), fmt
