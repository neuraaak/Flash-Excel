# ///////////////////////////////////////////////////////////////
# RELEASE - Publishes a GitHub Release (installer + zip) through the gh CLI
# ///////////////////////////////////////////////////////////////

"""Publish a GitHub Release for flash-excel with the local `gh` CLI.

Reads the version from [project] in pyproject.toml, resolves the artifacts
produced by `build.py` (the Inno Setup installer + the dist zip), shows the
title exactly as it will be created, asks for confirmation, then creates the
release attached to the `vX.Y.Z` tag.

Prerequisites:
    - `gh` installed and authenticated (`gh auth login`)
    - the artifacts already built: `uv run build.py`

Usage:
    uv run .scripts/build/release.py            # interactive confirmation
    uv run .scripts/build/release.py --yes       # no confirmation
    uv run .scripts/build/release.py --title "…"  # custom title
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"

# alpha / beta / rc / dev / a0 / b1 ... -> pre-release (aligned with 02-tag-sync.yml)
_PRERELEASE_RE = re.compile(r"(alpha|beta|rc|dev|a\d+|b\d+)")

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _force_utf8_stdout() -> None:
    """Avoid UnicodeEncodeError on a cp1252 Windows console."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _read_version() -> str:
    """Return [project].version from pyproject.toml."""
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]["version"]


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command and capture stdout/stderr (as text)."""
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def _fail(message: str) -> None:
    """Print an error and exit with code 1."""
    print(f"❌ {message}", file=sys.stderr)
    sys.exit(1)


def _resolve_assets(version: str) -> tuple[Path, Path, Path]:
    """Validate the artifacts and return (installer, source zip, versioned zip).

    The dist zip carries no version (`flash-excel.zip`): the final asset is a
    versioned copy, made only once the release is confirmed.
    """
    installer = PROJECT_ROOT / "dist" / "installer" / f"flash-excel-{version}-setup.exe"
    zip_src = PROJECT_ROOT / "dist" / "flash-excel.zip"

    if not installer.is_file():
        _fail(f"Installer not found: {installer}\n   -> run `uv run build.py` first.")
    if not zip_src.is_file():
        _fail(f"Zip not found: {zip_src}\n   -> run `uv run build.py` first.")

    return installer, zip_src, zip_src.with_name(f"flash-excel-{version}.zip")


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a flash-excel GitHub Release."
    )
    parser.add_argument(
        "--title", help='Release title (default: "Flash-Excel vX.Y.Z").'
    )
    parser.add_argument(
        "--yes", action="store_true", help="Do not ask for confirmation."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _force_utf8_stdout()

    if shutil.which("gh") is None:
        _fail("`gh` not found. Install the GitHub CLI, then `gh auth login`.")
    if _run(["gh", "auth", "status"]).returncode != 0:
        _fail("`gh` is not authenticated. Run `gh auth login`.")

    version = _read_version()
    tag = f"v{version}"
    title = args.title or f"Flash-Excel v{version}"
    is_prerelease = bool(_PRERELEASE_RE.search(version))

    # Never overwrite an existing release silently.
    if _run(["gh", "release", "view", tag]).returncode == 0:
        _fail(f"Release {tag} already exists. Delete it or change the version.")

    installer, zip_src, zip_versioned = _resolve_assets(version)
    tag_exists = (
        _run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"]).returncode == 0
    )

    # Summary + the title as-is, before acting.
    print("─" * 60)
    print("📦 GitHub Release to publish")
    print(
        f"   Tag        : {tag}" + ("" if tag_exists else "  (will be created by gh)")
    )
    print(f"   Title      : {title}")
    print(f"   Pre-release: {'yes' if is_prerelease else 'no'}")
    print("   Artifacts  :")
    for name in (installer.name, zip_versioned.name):
        print(f"     - {name}")
    print("─" * 60)

    answer = "y" if args.yes else input("Publish this release? [y/N] ").strip().lower()
    # "o"/"oui" stay accepted: the prompt is answered by a French-speaking
    # maintainer, and dropping them would reject a reflex keystroke.
    if answer not in {"y", "yes", "o", "oui"}:
        print("Cancelled.")
        return 1

    # Versioned copy of the zip only once publication is confirmed.
    shutil.copy2(zip_src, zip_versioned)

    cmd = ["gh", "release", "create", tag, "--title", title, "--generate-notes"]
    if is_prerelease:
        cmd.append("--prerelease")
    cmd += [str(installer), str(zip_versioned)]

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        _fail(f"`gh release create` failed (code {result.returncode}).")

    print(f"✅ Release {tag} published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
