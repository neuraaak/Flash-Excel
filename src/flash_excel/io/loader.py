# ///////////////////////////////////////////////////////////////
# LOADER - File reading functions (Excel and CSV)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
File loading utilities for flash-excel.

Provides functions to read Excel files (via the fastexcel/calamine
Rust backend) and CSV files (via Polars' native reader), plus
`read_schema`, which reads only what the UI needs to populate its column
dropdowns without materializing the full DataFrame.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import csv
from pathlib import Path

# Third-party imports
import polars as pl

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_EXCEL_SUFFIXES = frozenset({".xlsx", ".xls", ".xlsm"})
_UNEXPECTED_SHEET_PAYLOAD = "Unexpected sheet payload type from polars.read_excel()."
_UNEXPECTED_EXCEL_RESULT = "Unexpected return type from polars.read_excel()."

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def detect_separator(path: Path, default: str = ";") -> str:
    """Guess a CSV file's column separator from its first lines.

    Excel exports semicolons in French locales and commas elsewhere, and
    reading with the wrong one yields a single column holding the whole row.
    Falls back to ``default`` when the sample is undecidable — which is the
    case for a genuinely single-column file, where the separator is moot.

    Args:
        path: Path to the CSV file.
        default: Separator to return when detection fails.

    Returns:
        str: The detected separator, or ``default``.
    """
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            sample = handle.read(8192)
        return csv.Sniffer().sniff(sample, delimiters=";,	|").delimiter
    except (OSError, csv.Error):
        return default


def _first_sheet(result: pl.DataFrame | dict) -> pl.DataFrame | None:
    """Return the sheet polars gives back, whether as a frame or a {name: frame}.

    ``pl.read_excel`` returns a DataFrame for a single sheet and a dict when the
    sheet selector matches several, so every caller has to unwrap it.
    Returns ``None`` when the workbook holds no readable sheet.
    """
    if isinstance(result, pl.DataFrame):
        return result
    if isinstance(result, dict):
        if not result:
            return None
        first = next(iter(result.values()))
        if not isinstance(first, pl.DataFrame):
            raise TypeError(_UNEXPECTED_SHEET_PAYLOAD)
        return first
    raise TypeError(_UNEXPECTED_EXCEL_RESULT)


def read_excel(path: Path, sheet: int = 0) -> pl.DataFrame:
    """Read an Excel file into a Polars DataFrame.

    Uses the ``fastexcel`` backend (Rust/calamine) for performance.
    The file is fully materialized in memory.

    Args:
        path: Absolute or relative path to the ``.xlsx`` / ``.xls``
            file.
        sheet: Zero-based sheet index to read. Defaults to ``0``
            (first sheet).

    Returns:
        pl.DataFrame: DataFrame containing all rows and columns from
            the specified sheet.

    Raises:
        FileNotFoundError: If ``path`` does not point to an existing
            file.
        Exception: Propagates any error raised by the ``fastexcel``
            backend (e.g., corrupt file, unsupported format).

    Example:
        >>> from pathlib import Path
        >>> df = read_excel(Path("data/report.xlsx"), sheet=0)
        >>> df.shape
        (1500, 12)
    """
    df = _first_sheet(pl.read_excel(path, sheet_id=sheet, engine="calamine"))
    if df is None:
        raise ValueError("Excel file contains no readable sheets.")
    return df


def read_csv(
    path: Path,
    separator: str = ";",
    encoding: str = "utf8-lossy",
    decimal_comma: bool = False,
) -> pl.DataFrame:
    """Read a CSV file into a Polars DataFrame.

    Defaults to French-style semicolon-separated files with
    ``utf8-lossy`` encoding to absorb ``cp1252`` / ``latin-1``
    characters common in Excel exports.

    Args:
        path: Absolute or relative path to the CSV file.
        separator: Column delimiter character. Defaults to ``";"``.
        encoding: File encoding. Defaults to ``"utf8-lossy"`` which
            replaces invalid UTF-8 bytes rather than raising an error.
        decimal_comma: Parse ``1,5`` as a float. Off by default: a ``;`` file
            exported by a program still uses a dot, and turning this on would
            read those numbers as text. It is a per-preset opt-in for files
            that really come out of a French Excel.

    Returns:
        pl.DataFrame: DataFrame with all rows parsed from the CSV.

    Raises:
        FileNotFoundError: If ``path`` does not point to an existing
            file.
        polars.exceptions.ComputeError: If the file cannot be parsed
            with the given separator or encoding.

    Example:
        >>> from pathlib import Path
        >>> df = read_csv(Path("exports/data.csv"), separator=";")
        >>> df.shape
        (200, 5)
    """
    # infer_schema_length=None scans every row: with the default 100, a column
    # that is numeric at the top and textual further down fails the whole load.
    return pl.read_csv(
        path,
        separator=separator,
        encoding=encoding,
        infer_schema_length=None,
        decimal_comma=decimal_comma,
    )


def read_schema(path: Path, separator: str = ";") -> dict[str, str]:
    """Read inferred schema (column -> dtype name) for a source file.

    For Excel files, the first sheet's schema is used without reading its
    rows. For CSV files, Polars infers the schema from a bounded row sample.

    Args:
        path: Path to the source file.
        separator: CSV delimiter (ignored for Excel files).

    Returns:
        dict[str, str]: Mapping from column name to dtype name.
    """
    suffix = path.suffix.lower()

    if suffix in _EXCEL_SUFFIXES:
        # n_rows=1: calamine infers the dtypes from its own sample regardless,
        # so one row is enough here — reading the whole sheet just to show the
        # column dropdowns froze the window on large workbooks.
        df = _first_sheet(
            pl.read_excel(
                path,
                sheet_id=0,
                engine="calamine",
                read_options={"n_rows": 1},
            )
        )
        if df is None:
            return {}
        return {name: str(dtype) for name, dtype in df.schema.items()}

    # shortcut: the preview infers from the first 300 rows only, so a column
    # that turns textual further down shows its early type here while the run
    # (infer_schema_length=None) sees the real one. Upgrade to a full scan if a
    # mismatch ever confuses users — it costs a complete read per file pick.
    df = pl.read_csv(
        path,
        separator=separator,
        encoding="utf8-lossy",
        n_rows=300,
        infer_schema_length=None,
    )
    return {name: str(dtype) for name, dtype in df.schema.items()}


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "read_excel",
    "read_csv",
    "read_schema",
    "detect_separator",
]
