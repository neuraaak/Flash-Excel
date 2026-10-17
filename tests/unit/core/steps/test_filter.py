import polars as pl
import pytest

from flash_excel.core.models import FilterCondition
from flash_excel.core.steps.filter import filter_rows


def test_filter_rows_single_condition_gte():
    df = pl.DataFrame({"age": [15, 25, 30]})
    cond = FilterCondition(column="age", operator="gte", value=18)
    out = filter_rows(df, conditions=[cond])
    assert out["age"].to_list() == [25, 30]


def test_filter_rows_combine_and():
    df = pl.DataFrame({"age": [15, 25, 30], "statut": ["A", "A", "B"]})
    conds = [
        FilterCondition(column="age", operator="gte", value=18),
        FilterCondition(column="statut", operator="eq", value="A"),
    ]
    out = filter_rows(df, conditions=conds, combine="AND")
    assert out["age"].to_list() == [25]


def test_filter_rows_combine_or():
    df = pl.DataFrame({"age": [15, 25, 30], "statut": ["A", "A", "B"]})
    conds = [
        FilterCondition(column="age", operator="lt", value=16),
        FilterCondition(column="statut", operator="eq", value="B"),
    ]
    out = filter_rows(df, conditions=conds, combine="OR")
    assert out["age"].to_list() == [15, 30]


def test_filter_rows_string_value_coerced_to_numeric():
    df = pl.DataFrame({"age": [15, 25, 30]})
    cond = FilterCondition(column="age", operator="gte", value="18")
    out = filter_rows(df, conditions=[cond])
    assert out["age"].to_list() == [25, 30]


def test_filter_rows_invalid_combine_raises():
    df = pl.DataFrame({"age": [15]})
    cond = FilterCondition(column="age", operator="eq", value=15)
    with pytest.raises(ValueError, match="Invalid combine value"):
        filter_rows(df, conditions=[cond], combine="XOR")


def test_filter_rows_contains_is_literal_not_regex():
    df = pl.DataFrame({"name": ["C++ dev", "C+ dev", "Java dev"]})
    cond = FilterCondition(column="name", operator="contains", value="C++")
    out = filter_rows(df, conditions=[cond])
    assert out["name"].to_list() == ["C++ dev"]


def test_filter_rows_non_numeric_value_on_numeric_column_raises_readable_error():
    df = pl.DataFrame({"age": [15, 25]})
    cond = FilterCondition(column="age", operator="gte", value="18 ans")
    with pytest.raises(ValueError, match="is not a number"):
        filter_rows(df, conditions=[cond])
