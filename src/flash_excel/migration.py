# ///////////////////////////////////////////////////////////////
# MIGRATION - One-shot moves of user data out of the install dir
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Récupération des données utilisateur restées dans le dossier d'installation.

Jusqu'en 1.3.0, les presets étaient écrits dans ``{app}\\bin\\presets``. Ce
dossier est remplacé à chaque auto-update et supprimé à la désinstallation :
tout ce qui s'y trouve est en sursis. Au premier démarrage d'une version
récente, on rapatrie ce qui a survécu vers ``Documents\\flash-excel\\presets``.

Les réglages ne sont pas migrés : ``app.config.yaml`` était embarqué dans le
bundle, donc déjà écrasé par sa version par défaut au moment où ce code
s'exécute. Il n'y a rien à sauver, et le copier ne ferait que recopier des
valeurs par défaut.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import contextlib
import shutil

# Local imports
from flash_excel.logs import log
from flash_excel.paths import LEGACY_PRESETS_DIR, PRESETS_DIR

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def migrate_legacy_presets() -> int:
    """Copie les presets restés dans le dossier d'installation.

    Sans effet si l'ancien dossier n'existe pas. Un preset déjà présent dans
    la destination n'est jamais écrasé : le nouvel emplacement fait foi.
    L'ancien fichier est laissé en place — il disparaîtra avec la prochaine
    mise à jour, et le garder évite toute perte si la copie a échoué.

    Returns:
        int: Nombre de presets effectivement copiés.
    """
    if not LEGACY_PRESETS_DIR.is_dir():
        return 0

    migrated = 0
    # Une migration ratée ne doit pas empêcher l'application de démarrer.
    with contextlib.suppress(OSError):
        PRESETS_DIR.mkdir(parents=True, exist_ok=True)
        for source in sorted(LEGACY_PRESETS_DIR.glob("*.toml")):
            target = PRESETS_DIR / source.name
            if target.exists():
                continue
            with contextlib.suppress(OSError):
                shutil.copy2(source, target)
                migrated += 1

    if migrated:
        log("INFO", f"migration: {migrated} preset(s) copiés vers {PRESETS_DIR}")
    return migrated


__all__ = ["migrate_legacy_presets"]
