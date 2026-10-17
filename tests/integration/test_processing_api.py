from pathlib import Path

from flash_excel.core.models import DropColumnsStep, Preset, PresetMeta
from flash_excel.paths import DEFAULT_OUTPUT_DIR
from flash_excel.presets.store import save_preset
from flash_excel.ui.api import FlashExcelAPI


def test_resolve_keeps_extension():
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "keep", "folder": "./output/", "pattern": "{name}_clean"},
    )
    assert path.endswith("clients_clean.xlsx")


def test_resolve_changes_extension():
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "csv", "folder": "./output/", "pattern": "{name}_clean"},
    )
    assert path.endswith("clients_clean.csv")


def test_resolve_custom_pattern():
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/export_2024.xlsx",
        {"format": "keep", "folder": "/out/", "pattern": "processed_{name}"},
    )
    assert "processed_export_2024" in path


def test_resolve_output_format_returned():
    path, fmt = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "parquet", "folder": "./out/", "pattern": "{name}"},
    )
    assert fmt == "parquet"
    assert path.endswith(".parquet")


def test_resolve_keep_format_resolves_to_the_source_extension():
    """``write_dataframe`` rejects 'keep', so it must never leak out of here."""
    _, fmt = FlashExcelAPI._resolve_output_path(
        "/data/clients.csv",
        {"format": "keep", "folder": "/out/", "pattern": "{name}"},
    )
    assert fmt == "csv"


def test_resolve_anchors_a_relative_folder_outside_the_install_dir():
    """A relative folder must never resolve against the working directory."""
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "keep", "folder": "./output/", "pattern": "{name}_clean"},
    )
    resolved = Path(path)
    assert resolved.is_absolute()
    assert DEFAULT_OUTPUT_DIR in resolved.parents


def test_resolve_falls_back_to_the_default_folder_when_none_is_set():
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "keep", "folder": "", "pattern": "{name}_clean"},
    )
    assert Path(path).parent == DEFAULT_OUTPUT_DIR


def test_resolve_keeps_an_absolute_folder_untouched(tmp_path):
    path, _ = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "keep", "folder": str(tmp_path), "pattern": "{name}_clean"},
    )
    assert Path(path).parent == tmp_path


def test_run_worker_reports_progress_and_writes_the_processed_data(
    monkeypatch, tmp_path
):
    source = tmp_path / "source.csv"
    source.write_text("name;temporary\nAda;remove\n", encoding="utf-8")
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset(
            meta=PresetMeta(name="Test"),
            steps=[DropColumnsStep(action="drop_columns", columns=["temporary"])],
        ),
        preset_path,
    )
    api = FlashExcelAPI()
    events: list[tuple[str, dict]] = []
    writes: list[tuple[list[str], Path, str, str, str, bool]] = []
    monkeypatch.setattr(api, "_push", lambda event, data: events.append((event, data)))
    monkeypatch.setattr("flash_excel.ui.api.load_app_config", lambda: {"locale": "en"})
    monkeypatch.setattr(
        "flash_excel.io.writer.write_dataframe",
        lambda df, path, fmt, locale, separator, decimal_comma: writes.append(
            (df.columns, path, fmt, locale, separator, decimal_comma)
        ),
    )
    monkeypatch.setattr(
        "flash_excel.ui.api.resolve_csv_output", lambda _csv_config: (";", True)
    )

    api._run_worker(
        str(preset_path),
        [str(source)],
        {"format": "csv", "folder": str(tmp_path), "pattern": "{name}_clean"},
    )

    assert (
        "step",
        {"step_index": 0, "step_name": "drop_columns", "rows_in": 1, "rows_out": 1},
    ) in events
    assert [e for e, _ in events][-2:] == ["done", "batch_done"]
    assert events[-1][1]["succeeded"] == events[-1][1]["total"] == 1
    assert writes == [(["name"], tmp_path / "source_clean.csv", "csv", "en", ";", True)]


def test_run_worker_processes_every_file_and_stamps_its_index(monkeypatch, tmp_path):
    """A batch writes one output per source, each event tagged with its row."""
    sources = []
    for name in ("a", "b"):
        source = tmp_path / f"{name}.csv"
        source.write_text("name;temporary\nAda;remove\n", encoding="utf-8")
        sources.append(str(source))
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset(
            meta=PresetMeta(name="Test"),
            steps=[DropColumnsStep(action="drop_columns", columns=["temporary"])],
        ),
        preset_path,
    )
    api = FlashExcelAPI()
    events: list[tuple[str, dict]] = []
    writes: list[Path] = []
    monkeypatch.setattr(api, "_push", lambda event, data: events.append((event, data)))
    monkeypatch.setattr("flash_excel.ui.api.load_app_config", lambda: {"locale": "en"})
    monkeypatch.setattr(
        "flash_excel.io.writer.write_dataframe",
        lambda _df, path, *_args, **_kwargs: writes.append(path),
    )

    api._run_worker(
        str(preset_path),
        sources,
        {"format": "csv", "folder": str(tmp_path), "pattern": "{name}_clean"},
    )

    assert writes == [tmp_path / "a_clean.csv", tmp_path / "b_clean.csv"]
    assert len([event for event, _ in events if event == "done"]) == 2
    assert events[-1][1]["succeeded"] == 2


def test_a_failing_file_does_not_cancel_the_batch_under_skip(monkeypatch, tmp_path):
    """The default error mode keeps going: one locked file must not end a run."""
    broken = tmp_path / "broken.csv"
    broken.write_text("name\nAda\n", encoding="utf-8")
    good = tmp_path / "good.csv"
    good.write_text("name;temporary\nAda;remove\n", encoding="utf-8")
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset(
            meta=PresetMeta(name="Test"),
            steps=[DropColumnsStep(action="drop_columns", columns=["temporary"])],
        ),
        preset_path,
    )
    api = FlashExcelAPI()
    events: list[tuple[str, dict]] = []
    writes: list[Path] = []
    monkeypatch.setattr(api, "_push", lambda event, data: events.append((event, data)))
    monkeypatch.setattr("flash_excel.ui.api.load_app_config", lambda: {"locale": "en"})
    monkeypatch.setattr(
        "flash_excel.io.writer.write_dataframe",
        lambda _df, path, *_args, **_kwargs: writes.append(path),
    )

    api._run_worker(
        str(preset_path),
        [str(broken), str(good)],
        {
            "format": "csv",
            "folder": str(tmp_path),
            "pattern": "{name}_clean",
            "error_mode": "skip",
        },
    )

    assert writes == [tmp_path / "good_clean.csv"]
    assert events[-1][0] == "batch_done"
    assert (events[-1][1]["succeeded"], events[-1][1]["total"]) == (1, 2)


def test_error_mode_stop_ends_the_batch_at_the_first_failure(monkeypatch, tmp_path):
    broken = tmp_path / "broken.csv"
    broken.write_text("name\nAda\n", encoding="utf-8")
    good = tmp_path / "good.csv"
    good.write_text("name;temporary\nAda;remove\n", encoding="utf-8")
    preset_path = tmp_path / "preset.toml"
    save_preset(
        Preset(
            meta=PresetMeta(name="Test"),
            steps=[DropColumnsStep(action="drop_columns", columns=["temporary"])],
        ),
        preset_path,
    )
    api = FlashExcelAPI()
    writes: list[Path] = []
    monkeypatch.setattr(api, "_push", lambda *_args: None)
    monkeypatch.setattr("flash_excel.ui.api.load_app_config", lambda: {"locale": "en"})
    monkeypatch.setattr(
        "flash_excel.io.writer.write_dataframe",
        lambda _df, path, *_args, **_kwargs: writes.append(path),
    )

    api._run_worker(
        str(preset_path),
        [str(broken), str(good)],
        {
            "format": "csv",
            "folder": str(tmp_path),
            "pattern": "{name}_clean",
            "error_mode": "stop",
        },
    )

    assert writes == []


def test_push_stamps_the_file_being_processed(monkeypatch):
    """Every event must say which queue row it belongs to."""
    api = FlashExcelAPI()
    sent: list[str] = []
    monkeypatch.setattr(
        "flash_excel.ui.api.webview.windows",
        [type("W", (), {"evaluate_js": staticmethod(sent.append)})()],
    )

    api._file_index = 2
    api._push("done", {"rows_out": 7})

    assert '"file_index": 2' in sent[0]
    assert '"rows_out": 7' in sent[0]
