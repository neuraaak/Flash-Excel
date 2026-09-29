# ///////////////////////////////////////////////////////////////
# LOGS - Application logging setup (ezplog)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Canal de log unique de l'application, adossé à ezplog.

Les builds de production tournent en ``console = false`` : ``print()`` n'a
aucune destination et tout diagnostic disparaît. Ce module installe un
``Ezpl`` écrivant dans un fichier utilisateur, et ``hook_logger=True``
détourne au passage le ``logging`` stdlib (pywebview, polars, tufup) vers
le même fichier.

Le log ne doit jamais casser l'application : chaque appel est protégé, un
échec d'écriture est avalé.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import contextlib
from typing import Any

# Third-party imports
from ezplog import Ezpl

# Local imports
from flash_excel.paths import LOG_FILE

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Rotation quotidienne : loguru horodate lui-même l'archive au renommage
# (flash-excel.2026-09-30_00-18-10_321712.log), inutile de mettre un
# {time} dans le nom du fichier courant.
_ROTATION = "1 day"
_RETENTION = "14 days"

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def setup_logging(*, debug: bool = False) -> None:
    """Initialise le canal de log de l'application.

    Appelé une fois au démarrage, avant toute autre initialisation. Ezpl
    étant un singleton, un second appel est sans effet.

    Args:
        debug: Abaisse le niveau à DEBUG au lieu d'INFO.
    """
    # Un log indisponible (disque plein, dossier non inscriptible) ne doit
    # jamais empêcher l'application de démarrer.
    with contextlib.suppress(Exception):
        Ezpl(
            log_file=LOG_FILE,
            log_rotation=_ROTATION,
            log_retention=_RETENTION,
            file_logger_level="DEBUG" if debug else "INFO",
            hook_logger=True,
        )


def log(level: str, message: str) -> None:
    """Écrit une ligne dans le log applicatif.

    Initialise le canal à la volée si ``setup_logging`` n'a pas encore été
    appelé, pour qu'un import isolé (tests, script) n'ait pas à s'en soucier.

    Args:
        level: Niveau ezplog ("DEBUG", "INFO", "WARNING", "ERROR").
        message: Texte à journaliser.
    """
    with contextlib.suppress(Exception):
        if not Ezpl.is_initialized():
            setup_logging()
        logger: Any = Ezpl().get_logger()
        logger.log(level, message)


__all__ = ["log", "setup_logging"]
