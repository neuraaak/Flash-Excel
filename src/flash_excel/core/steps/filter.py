# ///////////////////////////////////////////////////////////////
# STEPS/FILTER - filter_rows step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: filter_rows.

Keeps only rows that satisfy a set of conditions. Each condition
targets a single column with a comparison operator and a scalar
value. Multiple conditions are combined with AND or OR logic.

Supported operators: eq, neq, gt, gte, lt, lte, contains,
startswith, endswith.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import TYPE_CHECKING

# Third-party imports
import polars as pl

# Local imports
from flash_excel.core.models import FilterCondition
from flash_excel.core.registry import action

if TYPE_CHECKING:
    from collections.abc import Callable

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Mapping from operator string to a lambda that builds a Polars expression.
# Each lambda receives (column_expr, value) and returns a pl.Expr.
_OPERATOR_MAP: dict[str, Callable[[pl.Expr, str | int | float], pl.Expr]] = {
    "eq": lambda col, v: col == v,
    "neq": lambda col, v: col != v,
    "gt": lambda col, v: col > v,
    "gte": lambda col, v: col >= v,
    "lt": lambda col, v: col < v,
    "lte": lambda col, v: col <= v,
    # literal=True: the user types plain text, not a regex — without it "C++"
    # also matches "C+ dev" and "." matches any character.
    "contains": lambda col, v: col.cast(pl.String).str.contains(str(v), literal=True),
    "startswith": lambda col, v: col.cast(pl.String).str.starts_with(str(v)),
    "endswith": lambda col, v: col.cast(pl.String).str.ends_with(str(v)),
}

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _coerce_value(
    value: str | int | float | bool, dtype: pl.DataType
) -> str | int | float | bool:
    """Cast a scalar value to match a Polars column dtype.

    Needed because filter values arrive as strings from the JS/TOML layer
    even when the target column is numeric.
    """
    if isinstance(value, str):
        try:
            if dtype.is_integer():
                return int(value)
            if dtype.is_float():
                return float(value)
        except ValueError:
            raise ValueError(
                f"'{value}' is not a number, but the column holds numbers "
                f"({dtype}). Enter a numeric value."
            ) from None
        if dtype == pl.Boolean:
            return value.lower() in ("true", "1", "yes")
    return value


def _build_expr(condition: FilterCondition) -> pl.Expr:
    """Translate a single FilterCondition into a Polars boolean expression.

    Args:
        condition: A validated filter condition from the preset model.

    Returns:
        pl.Expr: A boolean Polars expression for use with ``df.filter()``.

    Raises:
        ValueError: If the operator is not in the supported set.
    """
    builder = _OPERATOR_MAP.get(condition.operator)
    if builder is None:
        raise ValueError(
            f"Unsupported filter operator: '{condition.operator}'. "
            f"Valid operators: {list(_OPERATOR_MAP)}"
        )
    col_expr = pl.col(condition.column)
    return builder(col_expr, condition.value)


@action("filter_rows")
def filter_rows(
    df: pl.DataFrame,
    conditions: list[FilterCondition],
    combine: str = "AND",
) -> pl.DataFrame:
    """Keep only rows satisfying all (AND) or any (OR) conditions.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        conditions: List of filter conditions. Must contain at least
            one entry.
        combine: How to combine multiple conditions. ``"AND"`` keeps
            rows that match every condition; ``"OR"`` keeps rows that
            match at least one.

    Returns:
        pl.DataFrame: Filtered DataFrame with only matching rows.

    Raises:
        ValueError: If ``combine`` is not ``"AND"`` or ``"OR"``, or if
            an unsupported operator is encountered.
        polars.exceptions.ColumnNotFoundError: If a referenced column
            does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> from flash_excel.core.models import FilterCondition
        >>> df = pl.DataFrame({"age": [15, 25, 30], "statut": ["A", "A", "B"]})
        >>> cond = FilterCondition(column="age", operator="gte", value=18)
        >>> filter_rows(df, conditions=[cond], combine="AND")
        shape: (2, 2)
    """
    if not conditions:
        return df

    schema = df.schema
    coerced = []
    for cond in conditions:
        if isinstance(cond, dict):
            cond = FilterCondition(**cond)
        if cond.column in schema and isinstance(cond.value, str):
            cond = FilterCondition(
                column=cond.column,
                operator=cond.operator,
                value=_coerce_value(cond.value, schema[cond.column]),
            )
        coerced.append(cond)

    exprs = [_build_expr(cond) for cond in coerced]

    if combine == "AND":
        # Fold all expressions with bitwise AND.
        combined = exprs[0]
        for expr in exprs[1:]:
            combined = combined & expr
    elif combine == "OR":
        # Fold all expressions with bitwise OR.
        combined = exprs[0]
        for expr in exprs[1:]:
            combined = combined | expr
    else:
        raise ValueError(f"Invalid combine value: '{combine}'. Expected 'AND' or 'OR'.")

    return df.filter(combined)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["filter_rows"]
