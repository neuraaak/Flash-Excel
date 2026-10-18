from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.smoke


def test_ui_app_module_imports_without_error():
    import flash_excel.ui.app as app_module

    assert hasattr(app_module, "run")


def test_ui_app_uses_the_flash_blue_dark_icon():
    import flash_excel.ui.app as app_module

    assert app_module._ICON.name == "flash-blue-dark.ico"


def test_ui_app_persists_webview_storage(monkeypatch, tmp_path):
    import flash_excel.ui.app as app_module

    captured: dict[str, object] = {}

    class Event:
        def __iadd__(self, _handler):
            return self

    window = SimpleNamespace(
        dom=SimpleNamespace(body=SimpleNamespace(events=SimpleNamespace())),
        events=SimpleNamespace(loaded=Event()),
    )
    monkeypatch.setattr(app_module, "USER_CONFIG_DIR", tmp_path)
    monkeypatch.setattr(app_module, "setup_logging", lambda **_kwargs: None)
    monkeypatch.setattr(app_module, "log", lambda *_args: None)
    monkeypatch.setattr(app_module, "migrate_legacy_presets", lambda: None)
    monkeypatch.setattr(app_module, "consume_installer_locale", lambda: None)
    monkeypatch.setattr(app_module.webview, "create_window", lambda **_kwargs: window)
    monkeypatch.setattr(
        app_module.webview, "start", lambda **kwargs: captured.update(kwargs)
    )

    app_module.run()

    assert captured["private_mode"] is False
    assert captured["storage_path"] == str(tmp_path / "webview")


def test_flash_excel_api_instantiates_without_crash():
    from flash_excel.ui.api import FlashExcelAPI

    api = FlashExcelAPI()
    assert api._loaded_file is None
    assert api._source_columns == []
