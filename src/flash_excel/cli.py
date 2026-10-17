# ///////////////////////////////////////////////////////////////
# CLI - Headless pipeline runner
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Run a preset over one or more files without opening the window.

This is the entry point for anything that is not a person clicking: the
Windows Task Scheduler, a batch file, a CI step. Scheduling is deliberately
left to the scheduler — it survives a reboot, runs without a session, and
reports failures, none of which a desktop application does well.

Exit codes: ``0`` every file succeeded, ``1`` at least one failed, ``2``
the arguments were unusable (argparse).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import argparse
import sys
from pathlib import Path

# Third-party imports
import polars as pl

# Local imports
from flash_excel.config import load_app_config, resolve_csv_output
from flash_excel.core.models import Preset
from flash_excel.core.pipeline import run_pipeline
from flash_excel.io.loader import detect_separator, read_csv, read_excel
from flash_excel.io.writer import resolve_output_path, write_dataframe
from flash_excel.logs import log, setup_logging
from flash_excel.presets import load_preset

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_FORMATS = ("keep", "xlsx", "csv", "parquet")
_EXCEL_SUFFIXES = frozenset({".xlsx", ".xls", ".xlsm"})

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _attach_console() -> None:
    """Reuse the calling terminal's console, if there is one.

    The packaged application is built windowed (``console = false``), so a
    frozen run has no stdout and every print vanishes. Attaching to the
    parent console gives the output back when the executable is launched
    from a prompt, and is a no-op when there is no parent — a scheduled task,
    or a plain double-click.
    """
    if not getattr(sys, "frozen", False) or sys.platform != "win32":
        return
    import contextlib
    import ctypes

    ATTACH_PARENT_PROCESS = -1
    if not ctypes.windll.kernel32.AttachConsole(ATTACH_PARENT_PROCESS):
        return
    with contextlib.suppress(OSError):
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)  # noqa: SIM115
        sys.stderr = sys.stdout


def _read_source(source: Path, preset: Preset) -> pl.DataFrame:
    """Load one source file with the input settings carried by the preset."""
    if source.suffix.lower() in _EXCEL_SUFFIXES:
        return read_excel(source)
    separator = preset.meta.csv_separator or detect_separator(source)
    return read_csv(
        source,
        separator,
        preset.meta.csv_encoding,
        preset.meta.csv_decimal_comma,
    )


def build_parser() -> argparse.ArgumentParser:
    """Return the headless-run argument parser."""
    parser = argparse.ArgumentParser(
        prog="flash-excel",
        description="Apply a preset to one or more files, without the window.",
    )
    parser.add_argument(
        "--preset", required=True, type=Path, help="Path to the .toml preset."
    )
    parser.add_argument(
        "--input",
        required=True,
        nargs="+",
        type=Path,
        help="One or more source files. Each is processed independently.",
    )
    parser.add_argument("--output", type=Path, default=None, help="Destination folder.")
    parser.add_argument(
        "--format", choices=_FORMATS, default="keep", help="Output format."
    )
    parser.add_argument(
        "--pattern",
        default="{name}_clean",
        help="Output stem, where {name} is the source stem.",
    )
    parser.add_argument("--debug", action="store_true", help="Verbose logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the preset over every input file and return a process exit code."""
    _attach_console()
    args = build_parser().parse_args(argv)
    setup_logging(debug=args.debug)

    preset = load_preset(args.preset)
    app_config = load_app_config()
    separator, decimal_comma = resolve_csv_output(app_config.get("csv"))
    locale = app_config.get("locale", "en")

    failures = 0
    for source in args.input:
        # One bad file must not cancel the rest of the batch: a scheduled run
        # over a folder would otherwise stop at the first file still open in
        # Excel.
        try:
            df = run_pipeline(_read_source(source, preset), preset)
            out_path, fmt = resolve_output_path(
                source, args.format, args.output, args.pattern
            )
            write_dataframe(df, out_path, fmt, locale, separator, decimal_comma)
            message = f"{source.name} -> {out_path} ({len(df)} rows)"
            log("INFO", message)
            print(message)
        except Exception as exc:
            failures += 1
            message = f"{source.name} FAILED: {exc}"
            log("ERROR", message)
            print(message, file=sys.stderr)

    return 1 if failures else 0


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["build_parser", "main"]
