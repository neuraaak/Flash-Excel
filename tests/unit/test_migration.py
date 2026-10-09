"""Tests for the recovery of presets left behind in the install directory."""

from __future__ import annotations

import flash_excel.migration as migration


def _redirect(monkeypatch, legacy, target):
    monkeypatch.setattr(migration, "LEGACY_PRESETS_DIR", legacy)
    monkeypatch.setattr(migration, "PRESETS_DIR", target)


def test_migrate_without_legacy_dir_does_nothing(monkeypatch, tmp_path):
    target = tmp_path / "documents" / "presets"
    _redirect(monkeypatch, tmp_path / "absent", target)

    assert migration.migrate_legacy_presets() == 0
    assert not target.exists()


def test_migrate_copies_toml_presets_only(monkeypatch, tmp_path):
    legacy = tmp_path / "bin" / "presets"
    legacy.mkdir(parents=True)
    (legacy / "rh.toml").write_text("name = 'rh'", encoding="utf-8")
    (legacy / "notes.txt").write_text("ignore", encoding="utf-8")
    target = tmp_path / "documents" / "presets"
    _redirect(monkeypatch, legacy, target)

    assert migration.migrate_legacy_presets() == 1
    assert (target / "rh.toml").read_text(encoding="utf-8") == "name = 'rh'"
    assert not (target / "notes.txt").exists()
    # The original is kept: a failed copy must not destroy anything.
    assert (legacy / "rh.toml").exists()


def test_migrate_never_overwrites_the_new_location(monkeypatch, tmp_path):
    legacy = tmp_path / "bin" / "presets"
    legacy.mkdir(parents=True)
    (legacy / "rh.toml").write_text("ancien", encoding="utf-8")
    target = tmp_path / "documents" / "presets"
    target.mkdir(parents=True)
    (target / "rh.toml").write_text("courant", encoding="utf-8")
    _redirect(monkeypatch, legacy, target)

    assert migration.migrate_legacy_presets() == 0
    assert (target / "rh.toml").read_text(encoding="utf-8") == "courant"
