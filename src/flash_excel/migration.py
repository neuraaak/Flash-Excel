# ///////////////////////////////////////////////////////////////
# MIGRATION - One-shot moves of user data out of the install dir
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Recovery of user data left behind in the installation directory.

Up to 1.3.0, presets were written to ``{app}\\bin\\presets``. That directory is
replaced on every auto-update and removed on uninstall: everything in it is
living on borrowed time. On the first start of a recent version, whatever
survived is brought back to ``Documents\\flash-excel\\presets``.

Settings are not migrated: ``app.config.yaml`` used to be bundled, so it has
already been overwritten by its default version by the time this code runs.
There is nothing to save, and copying it would only copy defaults around.
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
    """Copy the presets left behind in the installation directory.

    A no-op when the legacy directory does not exist. A preset already present
    at the destination is never overwritten: the new location is authoritative.
    The old file is left in place — it will go away with the next update, and
    keeping it avoids any loss should the copy have failed.

    Returns:
        int: Number of presets actually copied.
    """
    if not LEGACY_PRESETS_DIR.is_dir():
        return 0

    migrated = 0
    # A failed migration must not keep the application from starting.
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
        log("INFO", f"migration: {migrated} preset(s) copied to {PRESETS_DIR}")
    return migrated


__all__ = ["migrate_legacy_presets"]
