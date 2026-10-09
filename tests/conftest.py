# ///////////////////////////////////////////////////////////////
# CONFTEST - Pytest configuration and fixtures
# ///////////////////////////////////////////////////////////////

"""

This module provides common fixtures and pytest configuration used across
all test suites for consistent test execution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import tempfile
from collections.abc import Generator
from pathlib import Path

# Third-party imports
import polars as pl
import pytest

# ///////////////////////////////////////////////////////////////
# FIXTURES - ISOLATION
# ///////////////////////////////////////////////////////////////


@pytest.fixture(scope="session", autouse=True)
def _isolate_user_log() -> Generator[None]:
    """Divert the suite's logging away from the user's real log file.

    ``flash_excel.logs.log`` initialises Ezpl on the fly against the
    %LOCALAPPDATA% log directory: without this guard, the suite pollutes the
    diagnostic file of a real installation with tmp_path paths.

    The Ezpl singleton is claimed before any application import rather than
    replacing ``logs.log``: modules do ``from flash_excel.logs import log``, so
    each keeps its own reference and patching the original module would not
    reach them.
    """
    from ezplog import Ezpl

    # ignore_cleanup_errors: loguru keeps the sink open until the process ends,
    # and Windows refuses to delete a file that is still open.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        Ezpl(log_file=Path(tmp) / "tests.log", hook_logger=False)
        yield


# ///////////////////////////////////////////////////////////////
# FIXTURES - TEMPORARY RESOURCES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """
    Create a temporary directory for tests.

    Automatically creates and cleans up a temporary directory for each test,
    ensuring isolation and cleanup between tests.

    Yields:
        Path: Temporary directory path (created and accessible during test)

    Example:
        >>> def test_with_temp_dir(temp_dir):
        ...     test_file = temp_dir / "test.txt"
        ...     test_file.write_text("content")
        ...     assert test_file.exists()
    """
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """
    Provide a temporary file path inside the temporary directory.

    The file path is created but the file itself is not created automatically.
    Tests can decide how to use the path (create the file, or just use the path).

    Args:
        temp_dir: Temporary directory fixture (injected by pytest)

    Returns:
        Path: Path to a temporary file (not yet created)

    Example:
        >>> def test_temp_file(temp_file):
        ...     # File doesn't exist yet
        ...     assert not temp_file.exists()
        ...     # Test can create it
        ...     temp_file.write_text("test")
        ...     assert temp_file.exists()
    """
    return temp_dir / "temp_file"


@pytest.fixture
def sample_df() -> pl.DataFrame:
    """
    Provide a small representative DataFrame for step tests.

    Columns:
        id (int), nom (str), montant (float), statut (str)
    """
    return pl.DataFrame(
        {
            "id": [1, 2, 3],
            "nom": ["Alice", "Bob", "Alice"],
            "montant": [100.0, 200.0, 100.0],
            "statut": ["Actif", "Inactif", "Actif"],
        }
    )
