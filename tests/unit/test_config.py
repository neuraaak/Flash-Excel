import pytest

from flash_excel.config import (
    consume_installer_locale,
    load_app_config,
    load_themes,
    save_app_config,
)


def test_load_app_config_defaults_locale(monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    result = load_app_config()
    assert result["locale"] == "en"


def test_save_and_reload_locale(monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    save_app_config("blue-gray", "dark", "fr")
    result = load_app_config()
    assert result["locale"] == "fr"


def _isolate_themes(
    monkeypatch, tmp_path, shipped="palette:\n  blue-gray:\n    dark: {}\n"
):
    """Isole le catalogue embarqué et la copie utilisateur dans tmp_path."""
    bundled = tmp_path / "bundled" / "theme.config.yaml"
    bundled.parent.mkdir(parents=True)
    bundled.write_text(shipped, encoding="utf-8")
    monkeypatch.setattr("flash_excel.config.BUNDLED_THEMES_CONFIG", bundled)
    monkeypatch.setattr(
        "flash_excel.config.THEMES_CONFIG", tmp_path / "theme.config.yaml"
    )
    monkeypatch.setattr("flash_excel.config.THEMES_STAMP", tmp_path / ".theme.source")
    return bundled


def test_load_themes_seeds_the_user_copy(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    assert "blue-gray" in load_themes()
    assert (tmp_path / "theme.config.yaml").is_file()


def test_load_themes_keeps_user_edits_while_shipped_is_unchanged(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    load_themes()
    (tmp_path / "theme.config.yaml").write_text(
        "palette:\n  perso:\n    dark: {}\n", encoding="utf-8"
    )
    assert list(load_themes()) == ["perso"]


def test_load_themes_refreshes_when_shipped_catalogue_changes(monkeypatch, tmp_path):
    bundled = _isolate_themes(monkeypatch, tmp_path)
    load_themes()
    (tmp_path / "theme.config.yaml").write_text(
        "palette:\n  perso:\n    dark: {}\n", encoding="utf-8"
    )
    bundled.write_text(
        "palette:\n  blue-gray:\n    dark: {}\n  neuve:\n    dark: {}\n",
        encoding="utf-8",
    )
    assert sorted(load_themes()) == ["blue-gray", "neuve"]
    # L'édition de l'utilisateur n'est pas détruite, elle est mise de côté.
    assert (tmp_path / "theme.config.yaml.bak").is_file()


def test_unknown_palette_falls_back_to_default(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    cfg_file.write_text(
        "appearance:\n  palette: disparue\n  mode: dark\nlocale: fr\n", encoding="utf-8"
    )
    assert load_app_config()["appearance"]["palette"] == "blue-gray"


_FRENCH_MARKER = "[Setup]\nLanguage=french\n"
_ENGLISH_MARKER = "[Setup]\nLanguage=english\n"


def _marker(monkeypatch, tmp_path, body):
    path = tmp_path / "installer.ini"
    if body is not None:
        path.write_text(body, encoding="utf-8")
    monkeypatch.setattr("flash_excel.config.INSTALLER_MARKER", path)
    return path


def test_installer_locale_applies_on_first_run(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    marker = _marker(monkeypatch, tmp_path, _FRENCH_MARKER)
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", tmp_path / "app.config.yaml")

    assert consume_installer_locale() == "fr"
    assert load_app_config()["locale"] == "fr"
    assert not marker.exists()


def test_installer_locale_overrides_an_existing_config(monkeypatch, tmp_path):
    # warm-dark doit exister dans le catalogue, sinon le garde-fou palette la
    # remplace par le défaut et l'assertion d'apparence porterait à faux.
    _isolate_themes(
        monkeypatch,
        tmp_path,
        shipped="palette:\n  blue-gray:\n    dark: {}\n  warm-dark:\n    light: {}\n",
    )
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", tmp_path / "app.config.yaml")
    save_app_config("warm-dark", "light", "fr")
    marker = _marker(monkeypatch, tmp_path, _ENGLISH_MARKER)

    assert consume_installer_locale() == "en"
    result = load_app_config()
    assert result["locale"] == "en"
    # Seule la locale change : l'apparence choisie par l'utilisateur survit.
    assert result["appearance"] == {"palette": "warm-dark", "mode": "light"}
    assert not marker.exists()


def test_user_locale_survives_once_the_marker_is_consumed(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", tmp_path / "app.config.yaml")
    _marker(monkeypatch, tmp_path, _FRENCH_MARKER)
    consume_installer_locale()

    save_app_config("blue-gray", "dark", "en")
    # Plus de marqueur : le réglage de l'utilisateur n'est plus écrasé.
    assert consume_installer_locale() is None
    assert load_app_config()["locale"] == "en"


def test_no_marker_leaves_the_config_untouched(monkeypatch, tmp_path):
    _isolate_themes(monkeypatch, tmp_path)
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    _marker(monkeypatch, tmp_path, None)

    assert consume_installer_locale() is None
    assert not cfg_file.exists()


@pytest.mark.parametrize("body", ["[Setup]\nLanguage=klingon\n", "pas du tout un ini"])
def test_unusable_marker_is_dropped_without_touching_the_locale(
    monkeypatch, tmp_path, body
):
    _isolate_themes(monkeypatch, tmp_path)
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", tmp_path / "app.config.yaml")
    marker = _marker(monkeypatch, tmp_path, body)

    assert consume_installer_locale() is None
    assert load_app_config()["locale"] == "en"
    # Supprimé quand même : le garder rejouerait l'échec à chaque démarrage.
    assert not marker.exists()
