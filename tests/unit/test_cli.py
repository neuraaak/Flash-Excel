# ///////////////////////////////////////////////////////////////
# TEST - Headless CLI runner
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Batch behaviour and exit codes of the headless entry point."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from flash_excel.cli import main

_PRESET = """[meta]
name = "Clean"
csv_separator = ";"

[[steps]]
action = "drop_columns"
columns = ["temporary"]
"""


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A preset, two valid sources and one the preset cannot process."""
    (tmp_path / "clean.toml").write_text(_PRESET, encoding="utf-8")
    for name, value in (("a", 1.5), ("b", 2.25)):
        pl.DataFrame({"name": [name], "value": [value], "temporary": [1]}).write_csv(
            tmp_path / f"{name}.csv", separator=";"
        )
    # No "temporary" column: drop_columns raises, and the batch must go on.
    pl.DataFrame({"name": ["c"]}).write_csv(tmp_path / "broken.csv", separator=";")
    return tmp_path


def _run(workspace: Path, *sources: str, extra: list[str] | None = None) -> int:
    return main(
        [
            "--preset",
            str(workspace / "clean.toml"),
            "--input",
            *[str(workspace / s) for s in sources],
            "--output",
            str(workspace / "out"),
            *(extra or []),
        ]
    )


def test_batch_writes_one_output_per_source(workspace):
    assert _run(workspace, "a.csv", "b.csv") == 0
    written = sorted(p.name for p in (workspace / "out").iterdir())
    assert written == ["a_clean.csv", "b_clean.csv"]


def test_a_failing_source_does_not_cancel_the_others(workspace):
    """A file locked by Excel must not drop the rest of a scheduled run."""
    assert _run(workspace, "broken.csv", "a.csv") == 1
    assert (workspace / "out" / "a_clean.csv").exists()


def test_format_override_changes_the_extension(workspace):
    assert _run(workspace, "a.csv", extra=["--format", "parquet"]) == 0
    assert (workspace / "out" / "a_clean.parquet").exists()


def test_pattern_renames_the_output(workspace):
    assert _run(workspace, "a.csv", extra=["--pattern", "{name}-2026"]) == 0
    assert (workspace / "out" / "a-2026.csv").exists()


def test_missing_preset_is_a_usage_error(workspace):
    with pytest.raises(SystemExit) as excinfo:
        main(["--input", str(workspace / "a.csv")])
    assert excinfo.value.code == 2
