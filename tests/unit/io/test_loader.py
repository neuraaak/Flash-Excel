from pathlib import Path

import polars as pl
import pytest

from flash_excel.io.loader import (
    detect_separator,
    read_csv,
    read_excel,
    read_schema,
)
from flash_excel.io.writer import write_excel


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    path = tmp_path / "data.csv"
    path.write_text("nom;age\nAlice;30\nBob;25\nAlice;30\n", encoding="utf-8")
    return path


@pytest.fixture
def xlsx_file(tmp_path: Path) -> Path:
    path = tmp_path / "data.xlsx"
    df = pl.DataFrame({"nom": ["Alice", "Bob", "Alice"], "age": [30, 25, 30]})
    write_excel(df, path)
    return path


def test_read_csv_parses_semicolon_separated_file(csv_file):
    df = read_csv(csv_file, separator=";")
    assert df.columns == ["nom", "age"]
    assert df.shape == (3, 2)


def test_read_schema_csv_returns_dtype_mapping(csv_file):
    schema = read_schema(csv_file, separator=";")
    assert "nom" in schema
    assert "age" in schema


def test_read_csv_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_csv(Path("does/not/exist.csv"))


def test_read_excel_returns_dataframe(xlsx_file):
    df = read_excel(xlsx_file)
    assert df.columns == ["nom", "age"]
    assert df.shape == (3, 2)


def test_read_schema_excel_returns_dtype_mapping(xlsx_file):
    schema = read_schema(xlsx_file)
    assert "nom" in schema
    assert "age" in schema


def test_read_csv_infers_schema_over_every_row(tmp_path: Path):
    path = tmp_path / "late_text.csv"
    rows = ["code", *["12345"] * 120, "2A 123"]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    df = read_csv(path, separator=";")
    assert df.shape == (121, 1)
    assert df["code"].to_list()[-1] == "2A 123"


@pytest.mark.parametrize(
    "content, expected",
    [
        ("nom;age\nAlice;30\n", ";"),
        ("name,age\nAlice,30\n", ","),
        ("name\tage\nAlice\t30\n", "\t"),
        ('name,note\nAlice,"a;b"\n', ","),
    ],
)
def test_detect_separator_reads_the_real_delimiter(tmp_path: Path, content, expected):
    path = tmp_path / "s.csv"
    path.write_text(content, encoding="utf-8")
    assert detect_separator(path) == expected


def test_detect_separator_falls_back_on_a_single_column_file(tmp_path: Path):
    path = tmp_path / "one.csv"
    path.write_text("name\nAlice\nBob\n", encoding="utf-8")
    assert detect_separator(path) == ";"


def test_read_csv_with_a_detected_comma_separator(tmp_path: Path):
    path = tmp_path / "comma.csv"
    path.write_text("name,age\nAlice,30\nBob,41\n", encoding="utf-8")
    df = read_csv(path, detect_separator(path))
    assert df.columns == ["name", "age"]
    assert df.shape == (2, 2)
