"""Parity between the Python step models and the front-end step registry.

Every action a preset may legitimately contain is declared in three places:
the ``Step`` discriminated union, the ``REGISTRY`` of handlers, and
``web/js/steps-registry.js`` which drives the UI. These drifted apart once
already — ``drop_columns`` and ``fill_nulls`` were modelled, registered and
tested, yet had no editor, so they were reachable only by hand-writing a TOML
preset.
"""

import re
import typing

import pytest

from flash_excel.core import steps as _steps  # noqa: F401  # populates REGISTRY
from flash_excel.core.models import RECOMMENDED_ACTION_ORDER, Step
from flash_excel.core.registry import REGISTRY
from flash_excel.paths import PACKAGE_DIR

_STEPS_REGISTRY_JS = PACKAGE_DIR / "ui" / "web" / "js" / "steps-registry.js"


def _modelled_actions() -> set[str]:
    """Action literals of every member of the ``Step`` union."""
    members = typing.get_args(typing.get_args(Step)[0])
    return {typing.get_args(m.model_fields["action"].annotation)[0] for m in members}


def _ui_actions() -> set[str]:
    """Actions listed in STEP_ACTIONS on the JS side."""
    source = _STEPS_REGISTRY_JS.read_text(encoding="utf-8")
    block = re.search(r"STEP_ACTIONS = \[(.*?)\]", source, re.S)
    assert block is not None, "STEP_ACTIONS array not found"
    return set(re.findall(r"'([a-z_]+)'", block.group(1)))


def _ui_i18n_keys() -> dict[str, str]:
    """Mapping action -> i18n key from the JS registry."""
    source = _STEPS_REGISTRY_JS.read_text(encoding="utf-8")
    block = re.search(r"STEP_I18N_KEYS = \{(.*?)\n\}", source, re.S)
    assert block is not None, "STEP_I18N_KEYS object not found"
    return dict(re.findall(r"(\w+): '([^']+)'", block.group(1)))


def test_every_modelled_action_has_a_handler():
    assert _modelled_actions() <= set(REGISTRY)


def test_every_modelled_action_is_editable_in_the_ui():
    assert _modelled_actions() == _ui_actions()


def test_every_ui_action_has_an_i18n_key():
    keys = _ui_i18n_keys()
    assert _ui_actions() == set(keys)


@pytest.mark.parametrize("locale", ["en", "fr"])
def test_step_labels_and_descriptions_are_translated(locale):
    locale_file = PACKAGE_DIR / "ui" / "web" / "js" / "locales" / f"{locale}.js"
    translated = set(
        re.findall(r"^\s*'([^']+)':", locale_file.read_text(encoding="utf-8"), re.M)
    )
    for key in _ui_i18n_keys().values():
        assert key in translated, f"{key} missing from {locale}.js"
        assert f"{key}.desc" in translated, f"{key}.desc missing from {locale}.js"


def test_recommended_order_covers_every_modelled_action():
    assert set(RECOMMENDED_ACTION_ORDER) == _modelled_actions()
