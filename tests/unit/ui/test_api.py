import threading
from pathlib import Path

import pytest

from flash_excel.core.models import DropColumnsStep, Preset, PresetMeta
from flash_excel.presets.store import save_preset
from flash_excel.ui.api import FlashExcelAPI


@pytest.fixture
def api() -> FlashExcelAPI:
    return FlashExcelAPI()


def test_get_version_returns_ok_with_version(api):
    result = api.get_version()
    assert result["ok"] is True
    assert "version" in result["data"]


def test_check_update_not_frozen_reports_no_update(api):
    result = api.check_update()
    assert result == {
        "ok": True,
        "data": {"available": False, "version": None, "error": None},
    }


def test_apply_update_not_frozen_returns_error(api):
    result = api.apply_update()
    assert result["ok"] is False
    assert "packaged application" in result["error"]


def test_debug_log_returns_ok(api, monkeypatch):
    captured: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "flash_excel.ui.api.log",
        lambda level, message: captured.append((level, message)),
    )
    result = api.debug_log("hello")
    assert result == {"ok": True, "data": None}
    assert captured == [("INFO", "[js] hello")]


def test_get_app_config_returns_defaults(api, monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    result = api.get_app_config()
    assert result["ok"] is True
    assert result["data"]["locale"] == "en"


def test_save_app_config_persists_and_reloads(api, monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    result = api.save_app_config("blue-gray", "dark", "fr")
    assert result["ok"] is True
    assert api.get_app_config()["data"]["locale"] == "fr"


def test_get_themes_returns_dict(api, monkeypatch, tmp_path):
    themes_file = tmp_path / "theme.config.yaml"
    themes_file.write_text(
        "palette:\n  blue-gray:\n    primary: '#000'\n", encoding="utf-8"
    )
    monkeypatch.setattr("flash_excel.config.THEMES_CONFIG", themes_file)
    result = api.get_themes()
    assert result["ok"] is True
    assert "blue-gray" in result["data"]


def test_clear_file_resets_state(api):
    api._source_columns = ["a", "b"]
    api._source_schema = {"a": "Int64"}
    result = api.clear_file()
    assert result == {"ok": True, "data": None}
    assert api._source_columns == []
    assert api._source_schema == {}


def test_get_step_payload_returns_empty_dict_when_absent(api):
    result = api.get_step_payload("drop_columns")
    assert result == {"ok": True, "data": {}}


def test_set_step_payload_stores_then_clears_on_empty(api):
    api.set_step_payload("drop_columns", {"columns": ["a"]})
    assert api._step_payloads["drop_columns"] == {"columns": ["a"]}
    api.set_step_payload("drop_columns", {})
    assert "drop_columns" not in api._step_payloads


def test_get_source_columns_returns_current_list(api):
    api._source_columns = ["nom", "age"]
    result = api.get_source_columns()
    assert result == {"ok": True, "data": ["nom", "age"]}


def test_new_preset_creates_empty_preset(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    result = api.new_preset("Mon Preset")
    assert result["ok"] is True
    assert result["data"]["name"] == "Mon Preset"
    assert result["data"]["steps"] == []


def test_new_preset_empty_name_returns_error(api):
    result = api.new_preset("   ")
    assert result == {"ok": False, "error": "Preset name cannot be empty"}


def test_get_presets_lists_valid_presets(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    preset = Preset(
        meta=PresetMeta(name="Test"),
        steps=[DropColumnsStep(action="drop_columns", columns=["a"])],
    )
    save_preset(preset, tmp_path / "test.toml")
    result = api.get_presets()
    assert result["ok"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "Test"
    assert result["data"][0]["step_count"] == 1


def test_get_presets_skips_invalid_files(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    (tmp_path / "broken.toml").write_text("not [valid toml", encoding="utf-8")
    result = api.get_presets()
    assert result["ok"] is True
    assert result["data"] == []


def test_load_preset_reads_file_and_caches_state(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    preset = Preset(
        meta=PresetMeta(name="Test"),
        steps=[DropColumnsStep(action="drop_columns", columns=["a"])],
    )
    path = tmp_path / "test.toml"
    save_preset(preset, path)
    result = api.load_preset(str(path))
    assert result["ok"] is True
    assert result["data"]["name"] == "Test"
    assert api._current_preset_path == path
    assert "drop_columns" in api._step_payloads


def test_load_preset_missing_file_returns_error(api):
    result = api.load_preset("does/not/exist.toml")
    assert result["ok"] is False


def test_save_preset_persists_to_disk(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    result = api.save_preset(
        "Mon Preset", [{"action": "drop_columns", "columns": ["a"]}]
    )
    assert result["ok"] is True
    saved_path = Path(result["data"]["path"])
    assert saved_path.exists()
    assert saved_path.name == "mon_preset.toml"


def test_delete_preset_removes_file_and_clears_current(api, monkeypatch, tmp_path):
    monkeypatch.setattr("flash_excel.ui.api.PRESETS_DIR", tmp_path)
    path = tmp_path / "test.toml"
    path.write_text("", encoding="utf-8")
    api._current_preset_path = path
    result = api.delete_preset(str(path))
    assert result == {"ok": True, "data": None}
    assert not path.exists()
    assert api._current_preset_path is None


def test_load_file_path_reads_csv_and_updates_state(api, tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("nom;age\nAlice;30\n", encoding="utf-8")
    result = api._load_file_path(str(csv_path))
    assert result["ok"] is True
    assert result["data"]["columns"] == ["nom", "age"]
    assert api._source_columns == ["nom", "age"]
    assert api._source_file == "data.csv"


def test_load_file_path_missing_file_returns_error(api):
    result = api._load_file_path("does/not/exist.csv")
    assert result["ok"] is False


def test_name_to_filename_slugifies_special_characters():
    assert FlashExcelAPI._name_to_filename("  Rapport RH 2024 !!") == "rapport_rh_2024"


def test_preset_to_dict_aggregates_computed_column_items():
    from flash_excel.core.models import AddComputedColumnStep

    preset = Preset(
        meta=PresetMeta(name="Test"),
        steps=[
            AddComputedColumnStep(
                action="add_computed_column", target="a", expression="1"
            ),
            AddComputedColumnStep(
                action="add_computed_column", target="b", expression="2"
            ),
        ],
    )
    result = FlashExcelAPI._preset_to_dict(preset)
    assert len(result["steps"]) == 1
    assert result["steps"][0]["action"] == "add_computed_column"
    assert result["steps"][0]["items"] == [
        {"target": "a", "expression": "1"},
        {"target": "b", "expression": "2"},
    ]


def test_stop_run_sets_stop_event(api):
    assert not api._stop_event.is_set()
    result = api.stop_run()
    assert result == {"ok": True, "data": None}
    assert api._stop_event.is_set()


def test_run_preset_rejects_concurrent_run(api):
    block = threading.Event()

    def _busy() -> None:
        block.wait()

    api._run_thread = threading.Thread(target=_busy, daemon=True)
    api._run_thread.start()
    try:
        result = api.run_preset("preset.toml", "file.csv", {})
        assert result == {"ok": False, "error": "A run is already in progress"}
    finally:
        block.set()
        api._run_thread.join(timeout=1)
