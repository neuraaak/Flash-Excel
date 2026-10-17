# ///////////////////////////////////////////////////////////////
# STORE - Preset file management (list, save, delete)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Preset store utilities for flash-excel.

Provides filesystem-level operations for managing TOML preset files:
listing available presets in a directory, persisting a `Preset`
instance to disk via `tomli_w`, and removing a preset file.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import tomli_w

# Local imports
from flash_excel.core.models import Preset

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def list_presets(directory: Path) -> list[Path]:
    """Return a sorted list of ``.toml`` files in a directory.

    Only files with a ``.toml`` extension are included. The directory
    is not searched recursively. Paths are sorted alphabetically by
    filename.

    Args:
        directory: Path to the directory containing preset files.

    Returns:
        list[Path]: Sorted list of ``.toml`` file paths. Returns an
            empty list if the directory does not exist or contains no
            ``.toml`` files.

    Example:
        >>> from pathlib import Path
        >>> presets = list_presets(Path("presets/"))
        >>> [p.name for p in presets]
        ['nettoyage_rh.toml', 'rapport_mensuel.toml']
    """
    if not directory.exists():
        return []
    return sorted(directory.glob("*.toml"), key=lambda p: p.name)


def save_preset(preset: Preset, path: Path) -> None:
    """Serialize a Preset instance to a TOML file on disk.

    Creates any missing parent directories. Overwrites any existing
    file at ``path``. The TOML is produced by ``tomli_w`` from the
    Pydantic model's own ``model_dump`` output, so the written file
    always round-trips back through ``presets.parser.load_preset``.

    Optional fields left unset are omitted rather than written as a null
    (TOML has no null): the model defaults restore them on load.

    Args:
        preset: Validated Preset instance to persist.
        path: Destination path for the ``.toml`` file.

    Raises:
        OSError: If the file cannot be written (e.g., permission
            denied, disk full).
        ValueError: If the preset holds a value TOML cannot express,
            such as a ``replace_values`` mapping onto null.

    Example:
        >>> from pathlib import Path
        >>> from flash_excel.core.models import Preset, PresetMeta
        >>> p = Preset(meta=PresetMeta(name="Test"), steps=[])
        >>> save_preset(p, Path("presets/test.toml"))
    """
    try:
        toml_content = tomli_w.dumps(preset.model_dump(exclude_none=True))
    except TypeError as exc:
        # Nested nulls (e.g. a replace_values mapping onto null) survive
        # exclude_none, and TOML has no way to write them. Fail here rather
        # than emit a file that can never be read back.
        raise ValueError(
            f"The preset '{preset.meta.name}' holds a value that cannot be "
            f"saved to TOML (a null inside a step). Details: {exc}"
        ) from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(toml_content, encoding="utf-8")


def delete_preset(path: Path) -> None:
    """Delete a preset file from disk.

    If the file does not exist, this function is a no-op (no error
    is raised). Useful for idempotent cleanup operations.

    Args:
        path: Path to the ``.toml`` preset file to remove.

    Raises:
        OSError: If the path exists but cannot be removed (e.g.,
            permission denied).

    Example:
        >>> from pathlib import Path
        >>> delete_preset(Path("presets/obsolete.toml"))
    """
    if path.exists():
        path.unlink()


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "list_presets",
    "save_preset",
    "delete_preset",
]
