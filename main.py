# ///////////////////////////////////////////////////////////////
# MAIN - Application entry point
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Application entry point for flash-excel.

With no arguments (or only ``--debug``), the desktop window opens:

    python main.py

Given ``--preset``, the same executable runs headless instead, which is
what a scheduled task or a batch file calls:

    python main.py --preset clean.toml --input a.xlsx b.xlsx --output out/
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def dispatch(argv: list[str]) -> int:
    """Open the window, or run headless when a preset is given on the command line.

    A single executable serves both modes: the installer ships one .exe and
    the scheduler needs no second artefact to call. Each branch imports its
    own entry point, so a headless run never loads webview.

    Args:
        argv: Arguments without the program name.

    Returns:
        int: Process exit code.
    """
    if "--preset" in argv:
        from flash_excel.cli import main

        return main(argv)

    from flash_excel.ui.app import run

    run()
    return 0


# ///////////////////////////////////////////////////////////////
# MAIN SCRIPT
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    raise SystemExit(dispatch(sys.argv[1:]))
