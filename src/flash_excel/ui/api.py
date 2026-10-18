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
        # Index of the file currently being processed, stamped onto every
        # event so the queue rows can be updated independently.
        self._file_index: int = 0

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
        preset_sources: list[dict[str, str]] | None = None,
    ) -> dict:
        """Persist appearance, locale and CSV settings to app.config.yaml."""
        try:
            save_app_config(
                palette, mode, locale, csv_separator, csv_decimal, preset_sources
            )
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
            result = []
            sources = [(PRESETS_DIR, "Local", False)]
            for source in load_app_config()["presets"]["sources"]:
                directory = Path(source["path"])
                if not directory.is_dir():
                    log("WARNING", f"preset source unavailable: {directory}")
                    continue
                sources.append((directory, source["label"], True))
            for directory, label, read_only in sources:
                for p in list_presets(directory):
                    self._append_preset_row(result, p, label, read_only)
            return _ok(result)
        except Exception as exc:
            return _err(str(exc))

    @staticmethod
    def _append_preset_row(
        result: list[dict], p: Path, label: str, read_only: bool
    ) -> None:
        """Append one listed preset, retaining corrupt files for repair."""
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
                    "label": label,
                    "read_only": read_only,
                }
            )
            return
        result.append(
            {
                "name": preset.meta.name,
                "description": preset.meta.description or "",
                "step_count": len(preset.steps),
                "path": str(p),
                "label": label,
                "read_only": read_only,
            }
        )

    @staticmethod
    def _is_read_only_preset(path: Path) -> bool:
        """Return whether a path belongs to a configured source directory."""
        for source in load_app_config()["presets"]["sources"]:
            try:
                path.resolve().relative_to(Path(source["path"]).resolve())
            except ValueError:
                continue
            return True
        return False

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
            if old_path is not None and self._is_read_only_preset(old_path):
                return _err("Configured preset sources are read-only")
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
            if self._is_read_only_preset(path):
                return _err("Configured preset sources are read-only")
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

    def open_files_dialog(self) -> dict:
        """Open the native picker in multi-select mode and load the selection.

        Only the first file is read for its schema: the step editors are
        column-driven and a batch is meant to hold files of the same shape.
        Reading all of them would freeze the window for no gain.

        Returns:
            dict: ``{"files": [...]}``, the first entry carrying the schema.
        """
        try:
            window = webview.active_window()
            if window is None:
                return _err(_NO_ACTIVE_WINDOW)
            result = window.create_file_dialog(  # type: ignore[union-attr]
                FileDialog.OPEN,
                allow_multiple=True,
                file_types=("Supported files (*.xlsx;*.xls;*.xlsm;*.csv)",),
            )
            if not result:
                return _ok({"cancelled": True})

            first = self._load_file_path(result[0])
            if not first["ok"]:
                return first
            files = [first["data"]]
            files.extend(self._file_summary(Path(p)) for p in result[1:])
            return _ok({"files": files})
        except Exception as exc:
            return _err(str(exc))

    def on_file_drop(self, event: dict) -> None:
        """Load the files dropped onto the window and tell the front-end.

        pywebview resolves each dropped file to a real path under
        ``pywebviewFullPath``; the browser's own File object has none. Files
        the application cannot read are skipped rather than failing the whole
        drop, since a user dragging a folder's contents catches stray ones.

        Args:
            event: The DOM drop event relayed by pywebview.
        """
        paths = [
            file["pywebviewFullPath"]
            for file in event.get("dataTransfer", {}).get("files", [])
            if file.get("pywebviewFullPath")
        ]
        if not paths:
            return

        files: list[dict] = []
        for path in paths:
            try:
                if files:
                    files.append(self._file_summary(Path(path)))
                    continue
                # The first one the application can read is the file the step
                # editors take their columns from, so it is loaded in full.
                loaded = self._load_file_path(path)
                if loaded["ok"]:
                    files.append(loaded["data"])
            except Exception as exc:
                log("WARNING", f"dropped file ignored: {Path(path).name}: {exc}")

        if files:
            self._push("files_dropped", {"files": files})

    @staticmethod
    def _file_summary(path: Path) -> dict:
        """Queue-row metadata for a file whose schema is not read."""
        result = FileLoaderResult.from_path(path)
        return {
            "path": str(path),
            "file_name": result.file_name,
            "size_bytes": result.size_bytes,
            "file_type": result.file_type,
            "columns": [],
            "schema": {},
        }

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

    def get_schedule_command(
        self,
        preset_path: str,
        file_paths: list[str],
        output_config: dict,
        task_name: str | None = None,
        start_time: str = "08:00",
    ) -> dict:
        """Build a command for the user to register in Windows Task Scheduler."""
        from flash_excel.ui.scheduling import build_schedule_command

        try:
            return _ok(
                build_schedule_command(
                    preset_path, file_paths, output_config, task_name, start_time
                )
            )
        except Exception as exc:
            return _err(str(exc))

    def create_scheduled_task(
        self,
        preset_path: str,
        file_paths: list[str],
        output_config: dict,
        task_name: str,
        start_time: str,
        confirmed: bool = False,
    ) -> dict:
        """Register a daily task only after the UI's explicit confirmation."""
        import subprocess
        from shutil import which
        from tempfile import TemporaryDirectory

        from flash_excel.ui.scheduling import build_schedule_command, build_task_xml

        if confirmed is not True:
            return _err("Task creation requires confirmation")
        try:
            execution = build_schedule_command(
                preset_path, file_paths, output_config, task_name, start_time
            )
            if sys.platform != "win32":
                return _err("Task scheduling is only available on Windows")
            scheduler = which("schtasks")
            if scheduler is None:
                return _err("Windows Task Scheduler command was not found")
            with TemporaryDirectory(prefix="flash-excel-task-") as task_dir:
                task_file = Path(task_dir) / "task.xml"
                task_file.write_bytes(build_task_xml(execution))
                result = subprocess.run(
                    [
                        scheduler,
                        "/create",
                        "/tn",
                        execution["task_path"],
                        "/xml",
                        str(task_file),
                    ],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    encoding="oem",
                    errors="replace",
                    timeout=20,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    check=False,
                )
            if result.returncode:
                return _err(
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Windows could not create the task"
                )
            return _ok({"task_name": execution["task_name"], "start_time": start_time})
        except Exception as exc:
            return _err(str(exc))

    def create_execution_launcher(
        self,
        preset_path: str,
        file_paths: list[str],
        output_config: dict,
        name: str,
    ) -> dict:
        """Save a manual .cmd launcher using a native save dialog."""
        from flash_excel.ui.scheduling import build_schedule_command

        try:
            execution = build_schedule_command(
                preset_path, file_paths, output_config, name
            )
            window = webview.active_window()
            if window is None:
                return _err(_NO_ACTIVE_WINDOW)
            result = window.create_file_dialog(
                FileDialog.SAVE,
                save_filename=f"{execution['task_name']}.cmd",
                file_types=("Command files (*.cmd)",),
            )
            if not result:
                return _ok({"cancelled": True})
            dest = Path(
                str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            )
            if dest.suffix.lower() != ".cmd":
                return _err("The launcher filename must end in .cmd")
            dest.write_bytes(execution["launcher"].encode("utf-8"))
            return _ok({"dest": str(dest)})
        except Exception as exc:
            return _err(str(exc))

    def preview_preset(
        self, preset_path: str, file_path: str, limit: int = 100
    ) -> dict:
        """Transform up to 100 input rows without writing or changing run state."""
        from flash_excel.core.pipeline import run_pipeline

        if type(limit) is not int or not 1 <= limit <= 100:
            return _err("Preview limit must be an integer between 1 and 100")
        try:
            preset = load_preset(Path(preset_path))
            df = self._read_source(Path(file_path), preset).head(limit)
            result = run_pipeline(df, preset)
            return _ok(
                {"columns": result.columns, "rows": json.loads(result.write_json())}
            )
        except Exception as exc:
            return _err(str(exc))

    def run_preset(
        self,
        preset_path: str,
        file_paths: list[str],
        output_config: dict,
    ) -> dict:
        """Start pipeline execution over one or more files, in a background thread.

        Returns immediately. Progress is pushed via window.flashEvent(); every
        event carries the ``file_index`` it belongs to, and a final
        ``batch_done`` closes the run.
        """
        if self._run_thread is not None and self._run_thread.is_alive():
            return _err("A run is already in progress")
        if not file_paths:
            return _err("No input file")
        self._stop_event = threading.Event()
        self._run_thread = threading.Thread(
            target=self._run_worker,
            args=(preset_path, file_paths, output_config),
            daemon=True,
        )
        self._run_thread.start()
        return _ok()

    def stop_run(self) -> dict:
        """Request the running pipeline to stop after the current step."""
        self._stop_event.set()
        return _ok()

    def _push(self, event_type: str, data: dict) -> None:
        """Push an event to the JS layer via evaluate_js.

        The index of the file being processed is stamped here rather than at
        every call site, so the front-end can always route an event to its
        queue row.
        """
        data = {**data, "file_index": self._file_index}
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
        file_paths: list[str],
        output_config: dict,
    ) -> None:
        """Pipeline execution worker — runs in a background thread."""
        from flash_excel.presets import load_preset as _load_preset

        t_start = time.monotonic()
        error_mode = output_config.get("error_mode", "skip")
        succeeded = 0

        try:
            # The preset comes first: it carries the CSV separator and
            # encoding the read needs.
            preset = _load_preset(Path(preset_path))
        except Exception as exc:
            self._fatal(exc, t_start)
            return

        for index, file_path in enumerate(file_paths):
            self._file_index = index
            if self._stop_event.is_set():
                self._push("log", {"level": "warn", "key": "log.run_stopped"})
                break
            if self._process_one(Path(file_path), preset, output_config, error_mode):
                succeeded += 1
            elif error_mode == "stop":
                # "stop" is about the whole run, not just the current file:
                # going on would write outputs the user asked not to produce.
                break

        self._push(
            "batch_done",
            {
                "elapsed_s": round(time.monotonic() - t_start, 2),
                "succeeded": succeeded,
                "total": len(file_paths),
            },
        )

    def _process_one(
        self,
        src: Path,
        preset: Preset,
        output_config: dict,
        error_mode: str,
    ) -> bool:
        """Run the preset over one file. Returns False when it did not finish."""
        from flash_excel.io.writer import write_dataframe

        t_start = time.monotonic()
        try:
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

            self._push(
                "log",
                {
                    "level": "info",
                    "key": "log.preset_steps",
                    "params": {"name": preset.meta.name, "count": len(preset.steps)},
                },
            )

            df = self._run_steps(df, preset, error_mode)
            if df is None:
                return False

            out_path, fmt = self._resolve_output_path(str(src), output_config)
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

            self._push(
                "done",
                {
                    "elapsed_s": round(time.monotonic() - t_start, 2),
                    "rows_out": len(df),
                    "output_path": out_path,
                },
            )
            return True

        except Exception as exc:
            self._fatal(exc, t_start)
            return False

    def _fatal(self, exc: Exception, t_start: float) -> None:
        """Report an error that ended a file before its step loop could run."""
        elapsed = round(time.monotonic() - t_start, 2)
        # fatal: nothing follows this for that file, not even a "done".
        # Without the flag the UI stays on "running" forever under error_mode
        # "ignore" — which is where a source file locked by Excel lands.
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
        """Unpack the UI's output config onto ``writer.resolve_output_path``.

        Args:
            file_path: Absolute path to the source file.
            output_config: Dict with keys ``'format'``, ``'folder'``, ``'pattern'``.

        Returns:
            tuple[str, str]: The output path, and the format it resolved to.
        """
        from flash_excel.io.writer import resolve_output_path

        path, fmt = resolve_output_path(
            Path(file_path),
            output_config.get("format", "keep"),
            output_config.get("folder"),
            output_config.get("pattern", "{name}_clean"),
        )
        return str(path), fmt
