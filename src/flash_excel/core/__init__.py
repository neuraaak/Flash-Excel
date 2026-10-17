# ///////////////////////////////////////////////////////////////
# CORE/__INIT__ - Public API for the core layer
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Core layer public API.

Exposes the pipeline orchestrator, action registry, Pydantic models,
and step functions used to transform DataFrames via TOML presets.
This layer has zero dependencies on `ui/` or `io/`.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .models import (
    DropColumnsStep,
    FilterCondition,
    FilterRowsStep,
    Preset,
    PresetMeta,
    ReorderColumnsStep,
    SortRowsStep,
    Step,
)
from .pipeline import run_pipeline
from .registry import REGISTRY, action

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Models
    "DropColumnsStep",
    "FilterCondition",
    "FilterRowsStep",
    "Preset",
    "PresetMeta",
    "ReorderColumnsStep",
    "SortRowsStep",
    "Step",
    # Pipeline
    "run_pipeline",
    # Registry
    "REGISTRY",
    "action",
]
