"""Save → load round-trip for every step type.

The editor writes presets through ``save_preset`` and reads them back through
``load_preset``. Anything that survives one direction but not the other is
silent data loss, so each of the 12 registered actions is asserted to come back
identical, plus the ``[meta]`` block that carries the source-file context.
"""

from pathlib import Path

import pytest

from flash_excel.core.models import (
    AddComputedColumnStep,
    CastTypesStep,
    CleanTextStep,
    DeduplicateRowsStep,
    DropColumnsStep,
    FillNullsStep,
    FilterCondition,
    FilterRowsStep,
    Preset,
    PresetMeta,
    RenameColumnsStep,
    ReorderColumnsStep,
    ReplaceValuesStep,
    SelectColumnsStep,
    SortRowsStep,
    Step,
)
from flash_excel.presets.parser import load_preset
from flash_excel.presets.store import save_preset

ALL_STEPS: list[Step] = [
    RenameColumnsStep(action="rename_columns", mapping={"old": "new"}),
    SelectColumnsStep(action="select_columns", columns=["a", "b"]),
    DropColumnsStep(action="drop_columns", columns=["tmp"]),
    CastTypesStep(action="cast_types", casts={"amount": "float", "day": "date"}),
    CleanTextStep(
        action="clean_text", columns=["name"], ops=["trim", "accents"], case="upper"
    ),
    ReplaceValuesStep(action="replace_values", column="status", mapping={"Y": "Yes"}),
    # strategy="forward" leaves `value` unset: the case that used to write
    # `value = None` and produce a file tomllib refused to read.
    FillNullsStep(action="fill_nulls", columns=["country"], strategy="forward"),
    FillNullsStep(
        action="fill_nulls", columns=["city"], strategy="value", value="Unknown"
    ),
    AddComputedColumnStep(
        action="add_computed_column", target="full", expression="MAJUSCULE(nom)"
    ),
    FilterRowsStep(
        action="filter_rows",
        combine="OR",
        conditions=[
            FilterCondition(column="age", operator="gte", value=18),
            FilterCondition(column="city", operator="contains", value="C++"),
        ],
    ),
    DeduplicateRowsStep(action="deduplicate_rows", subset=["email"], keep="last"),
    SortRowsStep(action="sort_rows", by=["age", "name"], descending=[True, False]),
    ReorderColumnsStep(action="reorder_columns", columns=["b", "a"]),
]


@pytest.mark.parametrize("step", ALL_STEPS, ids=lambda s: s.action)
def test_each_step_type_survives_a_save_load_round_trip(step: Step, tmp_path: Path):
    preset = Preset(meta=PresetMeta(name="Round trip"), steps=[step])
    path = tmp_path / "preset.toml"

    save_preset(preset, path)

    assert load_preset(path) == preset


def test_full_preset_with_every_step_survives_a_round_trip(tmp_path: Path):
    preset = Preset(
        meta=PresetMeta(
            name="Everything",
            description="all 12 actions",
            csv_separator=",",
            csv_encoding="utf8",
            source_columns=["a", "b", "tmp"],
            source_types={"a": "String", "b": "Int64"},
            source_file="model.xlsx",
        ),
        steps=ALL_STEPS,
    )
    path = tmp_path / "everything.toml"

    save_preset(preset, path)

    assert load_preset(path) == preset


def test_source_file_is_persisted(tmp_path: Path):
    """``source_file`` used to be dropped by the hand-written serializer."""
    preset = Preset(meta=PresetMeta(name="T", source_file="model.xlsx"), steps=[])
    path = tmp_path / "meta.toml"

    save_preset(preset, path)

    assert load_preset(path).meta.source_file == "model.xlsx"


def test_value_toml_cannot_express_is_refused_not_corrupted(tmp_path: Path):
    """A null inside a mapping must raise, never produce an unreadable file."""
    preset = Preset(
        meta=PresetMeta(name="Nulls"),
        steps=[
            ReplaceValuesStep(action="replace_values", column="c", mapping={"X": None})
        ],
    )
    path = tmp_path / "nulls.toml"

    with pytest.raises(ValueError, match="cannot be saved to TOML"):
        save_preset(preset, path)
    assert not path.exists()
