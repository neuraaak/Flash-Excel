import pytest

pytestmark = pytest.mark.smoke


def test_main_module_imports_without_error():
    import main

    assert hasattr(main, "dispatch")


def test_dispatch_routes_a_preset_argument_to_the_headless_runner(monkeypatch):
    """The window must not open — and webview must not load — for a batch run."""
    import main

    seen: list[list[str]] = []
    monkeypatch.setattr(
        "flash_excel.cli.main", lambda argv: seen.append(argv) or 0, raising=True
    )

    assert main.dispatch(["--preset", "x.toml", "--input", "a.csv"]) == 0
    assert seen == [["--preset", "x.toml", "--input", "a.csv"]]
