# ///////////////////////////////////////////////////////////////
# BUILD - Compile flash-excel via ezcompiler (>= 4.1.0)
# ///////////////////////////////////////////////////////////////

r"""Build script for flash-excel.

Reads the configuration from [tool.ezcompiler] in pyproject.toml and runs the
whole pipeline: version -> compile -> zip -> installer -> signed TUF release.
Everything stays local.

This script never publishes. Pushing the signed TUF tree to the update
backend is a separate, explicit step, run once the build has been checked:

    .scripts\build\publish-update.cmd     (or: ezcompiler publish update)
    .scripts\build\publish-release.cmd    (or: ezcompiler publish release)

Prerequisites:
    - the TUF signing keys must be present (`ezcompiler tuf init` otherwise)
    - Inno Setup (ISCC.exe) for the installer stage

Usage:
    uv run build.py                  # full pipeline
    uv run build.py --skip-build     # reuse dist/ as-is (installer iteration)
    uv run build.py --skip-release   # no TUF release (rebuild a version)
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
from ezcompiler import EzCompiler
from ezcompiler.services import ConfigService, UpdaterService
from ezplog import Ezpl

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT = Path(__file__).resolve().parent

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _force_utf8_stdout() -> None:
    """Avoid UnicodeEncodeError from the ezplog output on a cp1252 console."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build flash-excel.")
    parser.add_argument(
        "--skip-release",
        action="store_true",
        help="Skip the TUF release stage (useful to rebuild an already "
        "published version without an 'already released' error).",
    )
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Skip the Inno Setup installer stage.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip version generation and compilation, reusing the existing "
        "build in output_folder (useful to iterate on the installer or the "
        "release without recompiling). Fails when no build is present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    _force_utf8_stdout()
    Ezpl()  # enables the ezplog output (printer/logger stay silent otherwise)

    # Single config from pyproject.toml (+ ezcompiler.yaml when present).
    config = ConfigService.build_compiler_config(
        pyproject_path=PROJECT_ROOT / "pyproject.toml",
        search_dir=PROJECT_ROOT,
    )

    # Generates the auto-update client files (settings.py/update.py/root.json)
    # next to main.py and bundles them. settings.py pins the current VERSION,
    # hence the regeneration on every build. root.json is copied from
    # .tufup/repo/metadata/ (the bundle's TUF trust anchor).
    updater_files = UpdaterService.generate(config, PROJECT_ROOT)
    config.include_files["files"].extend(str(f) for f in updater_files)

    compiler = EzCompiler(config)

    # version -> compile -> zip -> installer -> signed TUF release
    compiler.run_pipeline(
        console=config.console,
        skip_installer=args.skip_installer,
        skip_release=args.skip_release,
        skip_build=args.skip_build,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
