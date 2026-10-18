# ///////////////////////////////////////////////////////////////
# PIPELINE - Orchestrates execution of preset steps
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pipeline orchestrator for flash-excel.

Provides `run_pipeline` to execute all steps of a Preset against a
DataFrame. Column availability per step is computed client-side by
`web/js/components/ActionSteps.js`, which tracks types as well.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import polars as pl

# Local imports — importing the steps package is what runs every @action
# decorator, so it is the only thing that puts handlers in REGISTRY. It has no
# referenced name on purpose; removing it leaves run_pipeline dispatching
# against an empty dict.
from flash_excel.core import (
    steps as _steps_module,  # noqa: F401  # pyright: ignore[reportUnusedImport]
)
from flash_excel.core.models import Preset
from flash_excel.core.registry import REGISTRY

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def run_pipeline(df: pl.DataFrame, preset: Preset) -> pl.DataFrame:
    """Execute all steps of a preset against a DataFrame.

    Each step is dispatched to its registered function via the
    REGISTRY, passing all model fields (except ``action``) as
    keyword arguments.

    Args:
        df: Input DataFrame produced by the io/loader layer.
        preset: Validated Preset instance (from ``presets/parser``).

    Returns:
        pl.DataFrame: Transformed DataFrame after all steps have run.

    Raises:
        KeyError: If a step's ``action`` has no registered handler.
            This should not occur if all step modules are imported.
        polars.exceptions.ColumnNotFoundError: If a step references a
            column that was already removed by a preceding step.

    Example:
        >>> import polars as pl
        >>> from flash_excel.core.models import Preset, PresetMeta, DropColumnsStep
        >>> df = pl.DataFrame({"a": [1], "b": [2], "tmp": [3]})
        >>> preset = Preset(
        ...     meta=PresetMeta(name="test"),
        ...     steps=[DropColumnsStep(action="drop_columns", columns=["tmp"])],
        ... )
        >>> run_pipeline(df, preset)
        shape: (1, 2)
    """
    result = df
    for step in preset.steps:
        handler = REGISTRY.get(step.action)
        if handler is None:
            raise KeyError(
                f"No registered handler for action '{step.action}'. "
                "Ensure all step modules are imported before running the pipeline."
            )
        # Pass all step fields except 'action' as keyword arguments.
        kwargs = step.model_dump(exclude={"action"})
        result = handler(result, **kwargs)
    return result


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["run_pipeline"]
