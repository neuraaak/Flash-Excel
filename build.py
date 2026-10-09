# ///////////////////////////////////////////////////////////////
# BUILD - Compile + release flash-excel via ezcompiler (>= 4.1.0)
# ///////////////////////////////////////////////////////////////

"""Build and release script for flash-excel.

Reads the configuration from [tool.ezcompiler] in pyproject.toml, runs the
whole pipeline (version -> compile -> zip -> installer -> signed TUF release),
then pushes the signed TUF tree to the configured backend (Cloudflare R2).

R2 credentials are read from the environment (or from a local, gitignored
.env file):
    R2_ACCOUNT_ID (or R2_ENDPOINT), R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY

Prerequisites:
    - the TUF signing keys must be present (`ezcompiler tuf init` otherwise)
    - Inno Setup (ISCC.exe) for the installer stage

Usage:
    uv run build.py                # full pipeline + upload
    uv run build.py --no-upload    # build only, no remote push
    uv run build.py --skip-build   # reuse dist/ as-is (installer iteration)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import argparse
import os
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


def _load_dotenv(path: Path) -> None:
    """Load the KEY=VALUE lines of a .env into os.environ (without overriding)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


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
    parser = argparse.ArgumentParser(description="Build and release flash-excel.")
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Build only; skip the remote upload step.",
    )
    parser.add_argument(
        "--skip-release",
        action="store_true",
        help="Skip the TUF release stage (useful to rebuild an already "
        "published version without an 'already released' error). Implies "
        "--no-upload.",
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
    Ezpl()  # active l'affichage ezplog (sinon printer/logger silencieux)
    _load_dotenv(PROJECT_ROOT / ".env")

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

    # Publication (an explicit stage, separate from the pipeline): the public
    # part of the signed TUF tree -> R2. The installer zip is not published
    # here, release_destination = disk keeping it local.
    # Without a signed release there is nothing new to push, so skip it too.
    if not args.no_upload and not args.skip_release:
        compiler.publish_update()

    return 0


if __name__ == "__main__":
    sys.exit(main())
