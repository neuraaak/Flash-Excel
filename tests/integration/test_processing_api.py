from pathlib import Path

from flash_excel.paths import DEFAULT_OUTPUT_DIR
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
