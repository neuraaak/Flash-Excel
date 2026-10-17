# ///////////////////////////////////////////////////////////////
# MODELS - Pydantic v2 discriminated union models for pipeline steps
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pydantic v2 models for the flash-excel pipeline.

Defines all step models (DropColumns, FilterRows, ReorderColumns,
SortRows) using a discriminated union on the `action` field, plus
the top-level `Preset` and `PresetMeta` models that represent a
complete TOML preset file.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Annotated, Literal

# Third-party imports
from pydantic import BaseModel, Field, model_validator

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

ScalarValue = str | int | float | bool

# ///////////////////////////////////////////////////////////////
# EXECUTION ORDER (RECOMMENDED)
# ///////////////////////////////////////////////////////////////

# Recommended logical order for business actions.
# The pipeline still executes in preset order; this constant is meant
# for UI guidance and validation hints.
RECOMMENDED_ACTION_ORDER: tuple[str, ...] = (
    "rename_columns",
    "select_columns",
    "drop_columns",
    "cast_types",
    "clean_text",
    "replace_values",
    "fill_nulls",
    "add_computed_column",
    "filter_rows",
    "deduplicate_rows",
    "sort_rows",
    "reorder_columns",
)

# ///////////////////////////////////////////////////////////////
# STEP MODELS
# ///////////////////////////////////////////////////////////////


class DropColumnsStep(BaseModel):
    """Step that removes one or more columns from the DataFrame.

    Example:
        >>> step = DropColumnsStep(action="drop_columns", columns=["tmp", "id"])
    """

    action: Literal["drop_columns"]
    columns: list[str] = Field(..., min_length=1, description="Column names to drop.")


class RenameColumnsStep(BaseModel):
    """Step that renames one or more columns.

    Example:
        >>> step = RenameColumnsStep(
        ...     action="rename_columns",
        ...     mapping={"old_name": "new_name"},
        ... )
    """

    action: Literal["rename_columns"]
    mapping: dict[str, str] = Field(
        ..., min_length=1, description="Mapping from source column to target column."
    )


class SelectColumnsStep(BaseModel):
    """Step that keeps only the listed columns in the given order.

    Example:
        >>> step = SelectColumnsStep(
        ...     action="select_columns",
        ...     columns=["id", "name", "amount"],
        ... )
    """

    action: Literal["select_columns"]
    columns: list[str] = Field(
        ..., min_length=1, description="Columns to keep and order in the output."
    )


class CastTypesStep(BaseModel):
    """Step that casts one or more columns to target logical types.

    Example:
        >>> step = CastTypesStep(
        ...     action="cast_types",
        ...     casts={"amount": "float", "created_at": "date"},
        ... )
    """

    action: Literal["cast_types"]
    casts: dict[
        str,
        Literal["string", "int", "float", "bool", "date", "datetime"],
    ] = Field(..., min_length=1, description="Mapping column name -> target type.")


# ------------------------------------------------
# FILTER ROWS
# ------------------------------------------------


class FilterCondition(BaseModel):
    """A single filter condition applied to one column.

    Attributes:
        column: Target column name.
        operator: Comparison operator.
        value: Value to compare against (string, int, float, or bool).

    Example:
        >>> cond = FilterCondition(column="statut", operator="eq", value="Actif")
    """

    column: str
    operator: Literal[
        "eq",
        "neq",
        "gt",
        "gte",
        "lt",
        "lte",
        "contains",
        "startswith",
        "endswith",
    ]
    value: ScalarValue


class FilterRowsStep(BaseModel):
    """Step that keeps only rows matching a set of conditions.

    Multiple conditions are combined with AND or OR logic.

    Example:
        >>> step = FilterRowsStep(
        ...     action="filter_rows",
        ...     combine="AND",
        ...     conditions=[FilterCondition(column="age", operator="gte", value=18)],
        ... )
    """

    action: Literal["filter_rows"]
    combine: Literal["AND", "OR"] = "AND"
    conditions: list[FilterCondition] = Field(
        ..., min_length=1, description="List of filter conditions."
    )


class ReplaceValuesStep(BaseModel):
    """Step that replaces exact values in a target column.

    Example:
        >>> step = ReplaceValuesStep(
        ...     action="replace_values",
        ...     column="status",
        ...     mapping={"YES": "Yes", "NO": "No"},
        ... )
    """

    action: Literal["replace_values"]
    column: str
    mapping: dict[ScalarValue, ScalarValue | None] = Field(
        ..., min_length=1, description="Exact value replacements to apply."
    )


class FillNullsStep(BaseModel):
    """Step that fills null values using a selected strategy.

    Example:
        >>> step = FillNullsStep(
        ...     action="fill_nulls",
        ...     columns=["country"],
        ...     strategy="value",
        ...     value="Unknown",
        ... )
    """

    action: Literal["fill_nulls"]
    columns: list[str] = Field(..., min_length=1, description="Columns to process.")
    strategy: Literal["value", "forward", "backward"] = "value"
    value: ScalarValue | None = None

    @model_validator(mode="after")
    def _validate_value_strategy(self) -> FillNullsStep:
        """Require ``value`` when strategy is ``value``."""
        if self.strategy == "value" and self.value is None:
            raise ValueError("fill_nulls strategy 'value' requires a non-null 'value'.")
        return self


class AddComputedColumnStep(BaseModel):
    """Step that creates a computed column from an expression string.

    Example:
        >>> step = AddComputedColumnStep(
        ...     action="add_computed_column",
        ...     target="full_name",
        ...     expression="concat(first_name, ' ', last_name)",
        ... )
    """

    action: Literal["add_computed_column"]
    target: str
    expression: str = Field(..., min_length=1)


class DeduplicateRowsStep(BaseModel):
    """Step that removes duplicate rows based on all or selected columns.

    Example:
        >>> step = DeduplicateRowsStep(
        ...     action="deduplicate_rows",
        ...     subset=["email"],
        ...     keep="first",
        ... )
    """

    action: Literal["deduplicate_rows"]
    subset: list[str] = Field(
        default_factory=list,
        description="Subset of columns used for duplicate detection (all columns when empty).",
    )
    keep: Literal["first", "last", "none"] = "first"


class CleanTextStep(BaseModel):
    """Step that applies text cleaning operations to string columns.

    Example:
        >>> step = CleanTextStep(
        ...     action="clean_text",
        ...     columns=["name", "city"],
        ...     ops=["trim", "collapse"],
        ...     case="lower",
        ... )
    """

    action: Literal["clean_text"]
    columns: list[str] = Field(
        ..., min_length=1, description="String columns to clean."
    )
    ops: list[Literal["trim", "collapse", "accents", "special"]] = Field(
        default_factory=list,
        description="Cleaning operations to apply: trim, collapse, accents, special.",
    )
    case: Literal["none", "lower", "upper", "title"] = "none"


# ------------------------------------------------
# REORDER COLUMNS
# ------------------------------------------------


class ReorderColumnsStep(BaseModel):
    """Step that reorders columns to a specified sequence.

    Columns not listed are appended at the end in their original order.

    Example:
        >>> step = ReorderColumnsStep(
        ...     action="reorder_columns", columns=["nom", "prenom", "salaire"]
        ... )
    """

    action: Literal["reorder_columns"]
    columns: list[str] = Field(
        ..., min_length=1, description="Desired column order (leading columns)."
    )


# ------------------------------------------------
# SORT ROWS
# ------------------------------------------------


class SortRowsStep(BaseModel):
    """Step that sorts rows by one or more columns.

    Example:
        >>> step = SortRowsStep(
        ...     action="sort_rows", by=["salaire", "nom"], descending=True
        ... )
    """

    action: Literal["sort_rows"]
    by: list[str] = Field(..., min_length=1, description="Column names to sort by.")
    descending: bool | list[bool] = False

    @model_validator(mode="after")
    def _validate_descending_length(self) -> SortRowsStep:
        """Ensure per-column directions align with sort keys when provided."""
        if isinstance(self.descending, list) and len(self.descending) != len(self.by):
            raise ValueError("sort_rows descending list length must match 'by' length.")
        return self


# ///////////////////////////////////////////////////////////////
# DISCRIMINATED UNION
# ///////////////////////////////////////////////////////////////

# Pydantic v2 discriminated union — dispatch is driven by the
# literal `action` field present in every concrete step model.
Step = Annotated[
    AddComputedColumnStep
    | CastTypesStep
    | CleanTextStep
    | DeduplicateRowsStep
    | DropColumnsStep
    | FillNullsStep
    | FilterRowsStep
    | RenameColumnsStep
    | ReorderColumnsStep
    | ReplaceValuesStep
    | SelectColumnsStep
    | SortRowsStep,
    Field(discriminator="action"),
]

# ///////////////////////////////////////////////////////////////
# PRESET MODELS
# ///////////////////////////////////////////////////////////////


class PresetMeta(BaseModel):
    """Metadata section of a TOML preset file.

    Attributes:
        name: Human-readable preset name.
        description: Optional description of what the preset does.
        csv_separator: Column separator for CSV files. ``None`` (the default)
            means detect it from the file; set it to force one.
        csv_encoding: Encoding used when reading CSV files.
        source_columns: Cached source columns from the model file used
            to bootstrap step editors without reloading a file.
        source_types: Cached source schema (column -> logical/raw dtype)
            used to preserve cast step behavior without reloading a file.

    Example:
        >>> meta = PresetMeta(name="Rapport RH", description="Nettoyage mensuel")
    """

    name: str
    description: str = ""
    csv_separator: str | None = None
    csv_encoding: str = "utf8-lossy"
    source_columns: list[str] = Field(default_factory=list)
    source_types: dict[str, str] = Field(default_factory=dict)
    source_file: str = ""


class Preset(BaseModel):
    """Top-level model representing a complete flash-excel TOML preset.

    A preset consists of a `[meta]` section describing context and CSV
    options, plus an ordered list of `[[steps]]` to execute in sequence.

    Example:
        >>> preset = Preset(
        ...     meta=PresetMeta(name="Test"),
        ...     steps=[DropColumnsStep(action="drop_columns", columns=["tmp"])],
        ... )
    """

    meta: PresetMeta
    steps: list[Step] = Field(default_factory=list)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "AddComputedColumnStep",
    "CastTypesStep",
    "CleanTextStep",
    "DeduplicateRowsStep",
    "DropColumnsStep",
    "FillNullsStep",
    "FilterCondition",
    "FilterRowsStep",
    "Preset",
    "PresetMeta",
    "RECOMMENDED_ACTION_ORDER",
    "RenameColumnsStep",
    "ReorderColumnsStep",
    "ReplaceValuesStep",
    "ScalarValue",
    "SelectColumnsStep",
    "SortRowsStep",
    "Step",
]
