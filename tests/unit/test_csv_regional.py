# ///////////////////////////////////////////////////////////////
# TEST - Regional CSV output settings
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Resolution of the CSV delimiter and decimal mark, and their round-trip."""

from __future__ import annotations

import polars as pl
import pytest

from flash_excel.config import resolve_csv_output
from flash_excel.io.loader import read_csv
from flash_excel.io.writer import write_csv


@pytest.fixture(autouse=True)
def _french_machine(monkeypatch):
    """Pretend the machine has French regional settings."""
    regional = {"sList": ";", "sDecimal": ","}
    monkeypatch.setattr(
        "flash_excel.config._regional",
        lambda name, fallback: regional.get(name, fallback),
    )


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (None, (";", True)),
        ({}, (";", True)),
        ({"separator": "auto", "decimal": "auto"}, (";", True)),
        ({"separator": "comma", "decimal": "auto"}, (",", False)),
        ({"separator": "semicolon", "decimal": "dot"}, (";", False)),
        ({"separator": "tab", "decimal": "comma"}, ("\t", True)),
        ({"separator": "nonsense", "decimal": "nonsense"}, (";", True)),
    ],
)
def test_resolve_csv_output(config, expected):
    assert resolve_csv_output(config) == expected


def test_comma_separator_never_pairs_with_comma_decimal():
    """A comma delimiter plus a comma decimal would split every float."""
    separator, decimal_comma = resolve_csv_output(
        {"separator": "comma", "decimal": "comma"}
    )
    assert (separator, decimal_comma) == (",", False)


def test_french_csv_round_trip(tmp_path):
    """A ;/comma file written by the app reads back with the same values."""
    df = pl.DataFrame({"label": ["a"], "value": [1.5]})
    path = tmp_path / "out.csv"
    write_csv(df, path, separator=";", decimal_comma=True)

    assert path.read_text(encoding="utf-8").splitlines()[1] == "a;1,5"
    back = read_csv(path, separator=";", decimal_comma=True)
    assert back["value"].dtype == pl.Float64
    assert back["value"][0] == 1.5


def test_default_write_keeps_dot_decimals(tmp_path):
    """The writer default must not change for callers that pass nothing."""
    path = tmp_path / "out.csv"
    write_csv(pl.DataFrame({"value": [1.5]}), path)
    assert path.read_text(encoding="utf-8").splitlines()[1] == "1.5"
