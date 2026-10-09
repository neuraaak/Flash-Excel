import datetime

import polars as pl
import pytest

from flash_excel.core.steps.computed import add_computed_column


def test_bracket_syntax_allows_column_with_space():
    df = pl.DataFrame({"Nom Complet": ["alice"]})
    out = add_computed_column(df, "test", "MAJUSCULE([Nom Complet])")
    assert out["test"].to_list() == ["ALICE"]


def test_bracket_syntax_allows_column_starting_with_digit():
    df = pl.DataFrame({"2024_total": [3]})
    out = add_computed_column(df, "test", "ABS([2024_total])")
    assert out["test"].to_list() == [3]


def test_bracket_syntax_allows_special_characters():
    df = pl.DataFrame({"Prix (€)": [1.2]})
    out = add_computed_column(df, "test", "ARRONDI([Prix (€)], 0)")
    assert out["test"].to_list() == [1.0]


def test_bracket_syntax_combines_with_functions():
    df = pl.DataFrame({"N° Client": ["a"], "id": ["1"]})
    out = add_computed_column(df, "test", "CONCATENER([N° Client], id)")
    assert out["test"].to_list() == ["a1"]


def test_plain_identifier_columns_still_work():
    df = pl.DataFrame({"prenom": ["bob"], "nom": ["martin"]})
    out = add_computed_column(df, "test", "MAJUSCULE(CONCATENER(prenom, nom))")
    assert out["test"].to_list() == ["BOBMARTIN"]


# ///////////////////////////////////////////////////////////////
# ONE TEST PER CATALOG FUNCTION
# ///////////////////////////////////////////////////////////////


def test_concatener_joins_columns_with_separator():
    df = pl.DataFrame({"prenom": ["Alice"], "nom": ["Smith"]})
    out = add_computed_column(df, "test", 'CONCATENER(prenom, nom, sep=" ")')
    assert out["test"].to_list() == ["Alice Smith"]


def test_majuscule_uppercases_string_column():
    df = pl.DataFrame({"nom": ["alice"]})
    out = add_computed_column(df, "test", "MAJUSCULE(nom)")
    assert out["test"].to_list() == ["ALICE"]


def test_minuscule_lowercases_string_column():
    df = pl.DataFrame({"nom": ["ALICE"]})
    out = add_computed_column(df, "test", "MINUSCULE(nom)")
    assert out["test"].to_list() == ["alice"]


def test_gauche_takes_leftmost_characters():
    df = pl.DataFrame({"nom": ["Alice"]})
    out = add_computed_column(df, "test", "GAUCHE(nom, 3)")
    assert out["test"].to_list() == ["Ali"]


def test_droite_takes_rightmost_characters():
    df = pl.DataFrame({"nom": ["Alice"]})
    out = add_computed_column(df, "test", "DROITE(nom, 3)")
    assert out["test"].to_list() == ["ice"]


def test_nbcar_counts_string_length():
    df = pl.DataFrame({"nom": ["Alice"]})
    out = add_computed_column(df, "test", "NBCAR(nom)")
    assert out["test"].to_list() == [5]


def test_supprespace_strips_whitespace():
    df = pl.DataFrame({"nom": ["  Alice  "]})
    out = add_computed_column(df, "test", "SUPPRESPACE(nom)")
    assert out["test"].to_list() == ["Alice"]


def test_arrondi_rounds_to_given_decimals():
    df = pl.DataFrame({"prix": [1.2345]})
    out = add_computed_column(df, "test", "ARRONDI(prix, 2)")
    assert out["test"].to_list() == [1.23]


def test_abs_returns_absolute_value():
    df = pl.DataFrame({"delta": [-5]})
    out = add_computed_column(df, "test", "ABS(delta)")
    assert out["test"].to_list() == [5]


def test_multiplier_multiplies_column_by_scalar():
    df = pl.DataFrame({"prix": [10.0]})
    out = add_computed_column(df, "test", "MULTIPLIER(prix, 1.2)")
    assert out["test"].to_list() == [12.0]


def test_ajouter_sums_two_columns():
    df = pl.DataFrame({"a": [1], "b": [2]})
    out = add_computed_column(df, "test", "AJOUTER(a, b)")
    assert out["test"].to_list() == [3]


def test_annee_extracts_year_from_date():
    df = pl.DataFrame({"d": [datetime.date(2024, 3, 15)]})
    out = add_computed_column(df, "test", "ANNEE(d)")
    assert out["test"].to_list() == [2024]


def test_mois_extracts_month_from_date():
    df = pl.DataFrame({"d": [datetime.date(2024, 3, 15)]})
    out = add_computed_column(df, "test", "MOIS(d)")
    assert out["test"].to_list() == [3]


def test_jour_extracts_day_from_date():
    df = pl.DataFrame({"d": [datetime.date(2024, 3, 15)]})
    out = add_computed_column(df, "test", "JOUR(d)")
    assert out["test"].to_list() == [15]


def test_aujourd_hui_returns_todays_date():
    df = pl.DataFrame({"a": [1]})
    out = add_computed_column(df, "test", "AUJOURD_HUI()")
    assert out["test"].to_list() == [datetime.date.today()]


def test_si_returns_alors_branch_when_condition_true():
    df = pl.DataFrame({"age": [25]})
    out = add_computed_column(df, "test", 'SI(age >= 18, "majeur", "mineur")')
    assert out["test"].to_list() == ["majeur"]


def test_si_returns_sinon_branch_when_condition_false():
    df = pl.DataFrame({"age": [15]})
    out = add_computed_column(df, "test", 'SI(age >= 18, "majeur", "mineur")')
    assert out["test"].to_list() == ["mineur"]


# ///////////////////////////////////////////////////////////////
# SECURITY / ERROR PATHS
# ///////////////////////////////////////////////////////////////


def test_disallowed_name_raises_value_error():
    # 'os.system(...)' is never executed: the AST validator rejects the
    # disallowed 'os' name before eval() ever runs.
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="not allowed"):
        add_computed_column(df, "test", "os.system('ls')")


def test_forbidden_dunder_attribute_raises_value_error():
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="not allowed"):
        add_computed_column(df, "test", "a.__class__")


def test_invalid_syntax_raises_value_error():
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="Invalid syntax"):
        add_computed_column(df, "test", "MAJUSCULE(")


def test_non_expr_result_raises_type_error():
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(TypeError, match="Polars Expr"):
        add_computed_column(df, "test", "1 + 1")


def test_unknown_column_raises_name_error_wrapped_in_value_error():
    df = pl.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="not allowed"):
        add_computed_column(df, "test", "MAJUSCULE(missing)")
