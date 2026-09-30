# ///////////////////////////////////////////////////////////////
# BUILD - Compile + release flash-excel via ezcompiler (>= 4.0.0)
# ///////////////////////////////////////////////////////////////

"""Script de build et de release pour flash-excel.

Lit la configuration depuis [tool.ezcompiler] de pyproject.toml, exécute le
pipeline complet (version -> compile -> zip -> installer -> release TUF signée),
puis pousse l'arbre TUF signé vers le backend configuré (Cloudflare R2).

Credentials R2 lus depuis les variables d'environnement (ou un fichier .env
local, gitignoré) :
    R2_ACCOUNT_ID (ou R2_ENDPOINT), R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY

Prérequis :
    - clés de signature TUF présentes (`ezcompiler release init` sinon)
    - Inno Setup (ISCC.exe) pour l'étape installer

Usage :
    uv run build.py                # pipeline complet + upload
    uv run build.py --no-upload    # build seul, sans push distant
    uv run build.py --skip-build   # reprend dist/ tel quel (itération installeur)
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
    """Charge les lignes KEY=VALUE d'un .env dans os.environ (sans écraser)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _force_utf8_stdout() -> None:
    """Évite les UnicodeEncodeError de l'affichage ezplog sur console cp1252."""
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
        help="Skip the TUF release stage (utile pour re-builder une version "
        "déjà publiée sans erreur 'already released'). Implique --no-upload.",
    )
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Skip the Inno Setup installer stage.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip version generation and compilation, et reprend le build "
        "existant dans output_folder (utile pour itérer sur l'installeur ou "
        "la release sans recompiler). Échoue si aucun build n'est présent.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    _force_utf8_stdout()
    Ezpl()  # active l'affichage ezplog (sinon printer/logger silencieux)
    _load_dotenv(PROJECT_ROOT / ".env")

    # Config unique depuis pyproject.toml (+ ezcompiler.yaml si présent).
    config = ConfigService.build_compiler_config(
        pyproject_path=PROJECT_ROOT / "pyproject.toml",
        search_dir=PROJECT_ROOT,
    )

    # Génère les fichiers client d'auto-update (settings.py/update.py/root.json)
    # à côté de main.py et les embarque dans le bundle. settings.py fige la
    # VERSION courante, donc régénération à chaque build. root.json est copié
    # depuis .tufup/repo/metadata/ (ancre de confiance TUF du bundle).
    updater_files = UpdaterService.generate(config, PROJECT_ROOT)
    config.include_files["files"].extend(str(f) for f in updater_files)

    compiler = EzCompiler(config)

    # version -> compile -> zip -> installer -> release TUF signée
    compiler.run_pipeline(
        console=config.console,
        skip_installer=args.skip_installer,
        skip_release=args.skip_release,
        skip_build=args.skip_build,
    )

    # upload (étape explicite, séparée du pipeline) : arbre TUF -> R2.
    # Sans release signée, il n'y a rien de nouveau à pousser → on saute aussi.
    if not args.no_upload and not args.skip_release:
        compiler.upload()

    return 0


if __name__ == "__main__":
    sys.exit(main())
