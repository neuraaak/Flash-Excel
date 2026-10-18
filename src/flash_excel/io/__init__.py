# ///////////////////////////////////////////////////////////////
# IO/__INIT__ - Public API for the io layer
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
I/O layer public API.

Exposes file reading (Excel, CSV) and writing functions. This layer
sits between `ui/` and `core/`: it converts files to/from Polars
DataFrames. It has no dependency on `core/`.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .loader import read_csv, read_excel, read_schema
from .models import FileLoaderResult
from .writer import write_csv, write_excel

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "read_excel",
    "read_csv",
    "read_schema",
    "FileLoaderResult",
    "write_excel",
    "write_csv",
]
