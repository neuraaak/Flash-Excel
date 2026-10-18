import json
from datetime import date

import polars as pl
import pytest

from flash_excel.core.models import Preset
from flash_excel.presets.store import save_preset
from flash_excel.ui.api import FlashExcelAPI


@pytest.mark.parametrize("suffix", [".csv", ".xlsx"])
def test_preview_transforms_only_the_head_without_writing(tmp_path, suffix):
    source = tmp_path / f"source{suffix}"
    frame = pl.DataFrame({"value": range(150), "temporary": ["drop"] * 150})
    if suffix == ".csv":
        frame.write_csv(source, separator=";")
    else:
        frame.write_excel(source)
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset.model_validate(
            {
                "meta": {"name": "Preview", "csv_separator": ";"},
                "steps": [
                    {"action": "drop_columns", "columns": ["temporary"]},
                    {"action": "sort_rows", "by": ["value"], "descending": True},
                ],
            }
        ),
        preset_path,
    )
    original = source.read_bytes()

    result = FlashExcelAPI().preview_preset(str(preset_path), str(source))

    assert result["ok"] is True
    assert result["data"]["columns"] == ["value"]
    assert result["data"]["rows"] == [{"value": n} for n in reversed(range(100))]
    assert source.read_bytes() == original
    assert set(tmp_path.iterdir()) == {source, preset_path}


def test_preview_empty_result_keeps_the_columns(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("value\n1\n2\n", encoding="utf-8")
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset.model_validate(
            {
                "meta": {"name": "Empty"},
                "steps": [
                    {
                        "action": "filter_rows",
                        "conditions": [
                            {"column": "value", "operator": "gt", "value": 100},
                        ],
                    }
                ],
            }
        ),
        preset_path,
    )

    result = FlashExcelAPI().preview_preset(str(preset_path), str(source))

    assert result == {"ok": True, "data": {"columns": ["value"], "rows": []}}


def test_preview_honours_csv_decimal_settings(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("amount;name\n1,5;Ada\n2,5;Grace\n", encoding="utf-8")
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset.model_validate(
            {
                "meta": {
                    "name": "Decimal",
                    "csv_separator": ";",
                    "csv_decimal_comma": True,
                },
                "steps": [],
            }
        ),
        preset_path,
    )

    result = FlashExcelAPI().preview_preset(str(preset_path), str(source), limit=1)

    assert result["data"]["rows"] == [{"amount": 1.5, "name": "Ada"}]


def test_preview_serializes_dates_and_nulls(monkeypatch, tmp_path):
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset.model_validate({"meta": {"name": "Dates"}, "steps": []}), preset_path
    )
    api = FlashExcelAPI()
    monkeypatch.setattr(
        api,
        "_read_source",
        lambda *_: pl.DataFrame(
            {
                "date": [date(2026, 1, 2), None],
                "amount": [1.5, float("nan")],
            }
        ),
    )

    result = api.preview_preset(str(preset_path), "source.xlsx")

    assert result["ok"] is True
    assert json.loads(json.dumps(result, allow_nan=False))["data"]["rows"] == [
        {"date": "2026-01-02", "amount": 1.5},
        {"date": None, "amount": None},
    ]


@pytest.mark.parametrize("limit", [0, -1, 101, True, "100"])
def test_preview_rejects_invalid_limits(limit):
    result = FlashExcelAPI().preview_preset("preset.toml", "source.csv", limit)
    assert result["ok"] is False
    assert "limit" in result["error"].lower()


def test_preview_returns_bridge_error_for_missing_preset(tmp_path):
    result = FlashExcelAPI().preview_preset(
        str(tmp_path / "missing.toml"), "source.csv"
    )
    assert result["ok"] is False
    assert result["error"]
