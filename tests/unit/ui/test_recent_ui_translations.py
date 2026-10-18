"""Keep preview, shared sources and execution settings bilingual."""

import re

from flash_excel.paths import PACKAGE_DIR

_LOCALES = PACKAGE_DIR / "ui" / "web" / "js" / "locales"
_SOURCE_ACTION_KEYS = {
    "settings.add_preset_source",
    "settings.edit_preset_source",
    "settings.remove_preset_source",
    "settings.browse_preset_source",
    "settings.delete_preset_source_title",
    "settings.delete_preset_source_confirm",
}


def _translations(locale):
    source = (_LOCALES / f"{locale}.js").read_text(encoding="utf-8")
    entries = re.findall(r"^\s*'([^']+)':\s*'((?:\\.|[^'\\])*)',?\s*$", source, re.M)
    return {
        key: value
        for key, value in entries
        if key.startswith(("execution.", "proc.preview", "settings.preset_source"))
        or key in _SOURCE_ACTION_KEYS
    }


def test_recent_ui_has_matching_english_and_french_keys():
    english = _translations("en")
    french = _translations("fr")
    assert english
    assert english.keys() == french.keys()
    for key in ("execution.risk", "execution.remove_select", "proc.preview_empty"):
        assert key in english
        assert english[key] != french[key]


def test_recent_ui_preserves_interpolation_parameters_in_both_locales():
    english = _translations("en")
    french = _translations("fr")
    for key in english.keys() & french.keys():
        assert english[key].strip(), key
        assert french[key].strip(), key
        assert set(re.findall(r"\{(\w+)\}", english[key])) == set(
            re.findall(r"\{(\w+)\}", french[key])
        ), key
