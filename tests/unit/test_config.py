from flash_excel.config import load_app_config, load_themes, save_app_config


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
