# ///////////////////////////////////////////////////////////////
# WRITER - File writing functions (Excel and CSV)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
File writing utilities for flash-excel.

Provides functions to persist a transformed Polars DataFrame to
Excel (.xlsx) or CSV format. Output paths are created including
any missing parent directories.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import polars as pl

# Local imports
from flash_excel.paths import DEFAULT_OUTPUT_DIR

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


_EXCEL_DTYPE_FORMATS: dict = {
    pl.Date: "DD/MM/YYYY",
    pl.Datetime: "DD/MM/YYYY HH:MM:SS",
}


_BOOL_LABELS: dict = {
    "en": ("True", "False"),
    "fr": ("VRAI", "FAUX"),
}


def _coerce_booleans(df: pl.DataFrame, locale: str = "fr") -> pl.DataFrame:
    """Convert Boolean columns to localized True/False strings (Excel-friendly)."""
    bool_cols = [name for name, dtype in df.schema.items() if dtype == pl.Boolean]
    if not bool_cols:
        return df
    true_label, false_label = _BOOL_LABELS.get(locale, _BOOL_LABELS["fr"])
    return df.with_columns(
        [
            pl.when(pl.col(c))
            .then(pl.lit(true_label))
            .otherwise(pl.lit(false_label))
            .alias(c)
            for c in bool_cols
        ]
    )


def write_excel(df: pl.DataFrame, path: Path, locale: str = "fr") -> None:
    """Write a DataFrame to an Excel file (.xlsx).

    Boolean columns are converted to a localized True/False string. Date and
    Datetime columns receive locale-appropriate format strings. All other
    types are written natively via xlsxwriter.

    Args:
        df: DataFrame to write.
        path: Destination path for the ``.xlsx`` file.
        locale: UI locale (``"en"`` or ``"fr"``) driving the boolean labels.

    Raises:
        OSError: If the parent directory cannot be created or the file
            cannot be written (e.g., permission denied).

    Example:
        >>> import polars as pl
        >>> from pathlib import Path
        >>> df = pl.DataFrame({"nom": ["Alice"], "salaire": [50000]})
        >>> write_excel(df, Path("output/rapport.xlsx"))
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df = _coerce_booleans(df, locale)
    df.write_excel(path, dtype_formats=_EXCEL_DTYPE_FORMATS)


def write_csv(
    df: pl.DataFrame,
    path: Path,
    separator: str = ";",
    decimal_comma: bool = False,
) -> None:
    """Write a DataFrame to a CSV file.

    Creates any missing parent directories before writing. Overwrites
    the file if it already exists at ``path``. Uses semicolon as the
    default delimiter to match the French Excel convention.

    The delimiter and the decimal mark travel together: a French Excel reading
    a ``;`` file also expects ``1,5``, not ``1.5``, and shows a dotted column
    as text. Callers resolve both from the regional settings — see
    ``flash_excel.config.resolve_csv_output``.

    Args:
        df: DataFrame to write.
        path: Destination path for the CSV file.
        separator: Column delimiter character. Defaults to ``";"``.
        decimal_comma: Write floats with a comma decimal mark. Must stay
            ``False`` when ``separator`` is ``","``, or every float splits
            its own cell.

    Raises:
        OSError: If the parent directory cannot be created or the file
            cannot be written (e.g., permission denied).

    Example:
        >>> import polars as pl
        >>> from pathlib import Path
        >>> df = pl.DataFrame({"nom": ["Alice"], "salaire": [50000]})
        >>> write_csv(df, Path("output/rapport.csv"), separator=";")
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(path, separator=separator, decimal_comma=decimal_comma)


def write_parquet(df: pl.DataFrame, path: Path) -> None:
    """Write a DataFrame to a Parquet file.

    Creates any missing parent directories before writing.

    Args:
        df: DataFrame to write.
        path: Destination path for the ``.parquet`` file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)


def resolve_output_path(
    source: Path,
    fmt: str = "keep",
    folder: str | Path | None = None,
    pattern: str = "{name}_clean",
) -> tuple[Path, str]:
    """Compute where a run writes, and the format it resolved to.

    Args:
        source: The source file being processed.
        fmt: ``'keep'`` (reuse the source extension), ``'xlsx'``, ``'csv'``
            or ``'parquet'``.
        folder: Destination directory. ``None`` means the default output
            folder.
        pattern: Output stem, where ``{name}`` is the source stem.

    Returns:
        tuple[Path, str]: The output path, and the resolved format — never
            ``'keep'``, which ``write_dataframe`` cannot dispatch.
    """
    if fmt == "keep":
        fmt = source.suffix.lstrip(".") or "xlsx"
    base_name = pattern.replace("{name}", source.stem)
    # A relative folder would resolve against the working directory, which
    # for the installed app is the installation folder — replaced by every
    # auto-update. Anchor it to the user's Documents instead.
    destination = Path(folder) if folder else DEFAULT_OUTPUT_DIR
    if not destination.is_absolute():
        destination = DEFAULT_OUTPUT_DIR / destination
    return destination / f"{base_name}.{fmt}", fmt


def write_dataframe(
    df: pl.DataFrame,
    path: Path,
    fmt: str,
    locale: str = "fr",
    separator: str = ";",
    decimal_comma: bool = False,
) -> None:
    """Dispatch DataFrame writing based on format.

    Args:
        df: DataFrame to write.
        path: Destination path (extension must match fmt).
        fmt: One of ``'xlsx'``, ``'csv'``, ``'parquet'``. Never ``'keep'`` — resolve first.
        locale: UI locale (``"en"`` or ``"fr"``), forwarded to ``write_excel``
            for boolean label formatting. Ignored for ``'csv'``/``'parquet'``.
        separator: CSV delimiter. Ignored for ``'xlsx'``/``'parquet'``.
        decimal_comma: CSV decimal mark. Ignored for ``'xlsx'``/``'parquet'``.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    if fmt == "xlsx":
        write_excel(df, path, locale)
    elif fmt == "csv":
        write_csv(df, path, separator, decimal_comma)
    elif fmt == "parquet":
        write_parquet(df, path)
    else:
        raise ValueError(
            f"Unsupported format: {fmt!r}. Expected 'xlsx', 'csv', or 'parquet'."
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "resolve_output_path",
    "write_excel",
    "write_csv",
    "write_parquet",
    "write_dataframe",
]
