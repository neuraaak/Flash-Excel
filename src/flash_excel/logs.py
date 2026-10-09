# ///////////////////////////////////////////////////////////////
# LOGS - Application logging setup (ezplog)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""The application's single logging channel, backed by ezplog.

Production builds run with ``console = false``: ``print()`` has nowhere to go
and every diagnostic vanishes. This module installs an ``Ezpl`` writing to a
user-local file, and ``hook_logger=True`` also diverts the stdlib ``logging``
records (pywebview, polars, tufup) into that same file.

Logging must never break the application: every call is guarded, and a write
failure is swallowed.
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

# Daily rotation: loguru timestamps the archive itself when renaming it
# (flash-excel.2026-09-30_00-18-10_321712.log), so there is no need for a
# {time} placeholder in the name of the current file.
_ROTATION = "1 day"
_RETENTION = "14 days"

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def setup_logging(*, debug: bool = False) -> None:
    """Initialise the application logging channel.

    Called once at startup, before any other initialisation. Ezpl being a
    singleton, a second call has no effect.

    Args:
        debug: Lower the level to DEBUG instead of INFO.
    """
    # Unavailable logging (full disk, non-writable directory) must never keep
    # the application from starting.
    with contextlib.suppress(Exception):
        Ezpl(
            log_file=LOG_FILE,
            log_rotation=_ROTATION,
            log_retention=_RETENTION,
            file_logger_level="DEBUG" if debug else "INFO",
            hook_logger=True,
        )


def log(level: str, message: str) -> None:
    """Write one line to the application log.

    Initialises the channel on the fly when ``setup_logging`` has not been
    called yet, so an isolated import (tests, a script) need not care.

    Args:
        level: ezplog level ("DEBUG", "INFO", "WARNING", "ERROR").
        message: The text to log.
    """
    with contextlib.suppress(Exception):
        if not Ezpl.is_initialized():
            setup_logging()
        logger: Any = Ezpl().get_logger()
        logger.log(level, message)


__all__ = ["log", "setup_logging"]
