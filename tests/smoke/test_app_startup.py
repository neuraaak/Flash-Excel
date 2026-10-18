import pytest

pytestmark = pytest.mark.smoke


def test_ui_app_module_imports_without_error():
    import flash_excel.ui.app as app_module

    assert hasattr(app_module, "run")


def test_ui_app_uses_the_flash_blue_dark_icon():
    import flash_excel.ui.app as app_module

    assert app_module._ICON.name == "flash-blue-dark.ico"


def test_flash_excel_api_instantiates_without_crash():
    from flash_excel.ui.api import FlashExcelAPI

    api = FlashExcelAPI()
    assert api._loaded_file is None
    assert api._source_columns == []
