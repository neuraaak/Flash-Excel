import polars as pl

from flash_excel.core.models import (
    DropColumnsStep,
    Preset,
    PresetMeta,
)
from flash_excel.core.pipeline import run_pipeline


def test_run_pipeline_executes_steps_in_order():
    df = pl.DataFrame({"a": [1], "b": [2], "tmp": [3]})
    preset = Preset(
        meta=PresetMeta(name="test"),
        steps=[DropColumnsStep(action="drop_columns", columns=["tmp"])],
    )
    out = run_pipeline(df, preset)
    assert out.columns == ["a", "b"]


def test_run_pipeline_empty_steps_returns_input_unchanged():
    df = pl.DataFrame({"a": [1]})
    preset = Preset(meta=PresetMeta(name="test"), steps=[])
    out = run_pipeline(df, preset)
    assert out.equals(df)
