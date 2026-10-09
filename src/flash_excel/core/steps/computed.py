# ///////////////////////////////////////////////////////////////
# STEPS/COMPUTED - add_computed_column step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: add_computed_column.

Adds a new column to the DataFrame using an Excel-style expression
evaluated in a restricted namespace of named functions.
"""

from __future__ import annotations

import ast
import datetime
import re

import polars as pl

from flash_excel.core.registry import action

# ///////////////////////////////////////////////////////////////
# EXCEL-STYLE FUNCTION CATALOG
# ///////////////////////////////////////////////////////////////


def _make_namespace(df: pl.DataFrame) -> dict:
    """Build the restricted eval namespace with Excel-style functions + column refs."""

    # Uppercase names are intentional: they match Excel function conventions  # noqa: N802
    def CONCATENER(*parts: pl.Expr | str, sep: str = "") -> pl.Expr:  # noqa: N802
        coerced = [pl.lit(p) if isinstance(p, str) else p for p in parts]
        return pl.concat_str(coerced, separator=sep)

    def MAJUSCULE(col: pl.Expr) -> pl.Expr:
        return col.str.to_uppercase()  # noqa: N802

    def MINUSCULE(col: pl.Expr) -> pl.Expr:
        return col.str.to_lowercase()  # noqa: N802

    def GAUCHE(col: pl.Expr, n: int) -> pl.Expr:
        return col.str.slice(0, n)  # noqa: N802

    def DROITE(col: pl.Expr, n: int) -> pl.Expr:
        return col.str.slice(-n)  # noqa: N802

    def NBCAR(col: pl.Expr) -> pl.Expr:
        return col.str.len_chars()  # noqa: N802

    def SUPPRESPACE(col: pl.Expr) -> pl.Expr:
        return col.str.strip_chars()  # noqa: N802

    def ARRONDI(col: pl.Expr, n: int = 0) -> pl.Expr:
        return col.round(n)  # noqa: N802

    def ABS(col: pl.Expr) -> pl.Expr:
        return col.abs()  # noqa: N802

    def MULTIPLIER(col: pl.Expr, n: float) -> pl.Expr:
        return col * n  # noqa: N802

    def AJOUTER(col1: pl.Expr, col2: pl.Expr) -> pl.Expr:
        return col1 + col2  # noqa: N802

    def ANNEE(col: pl.Expr) -> pl.Expr:
        return col.dt.year()  # noqa: N802

    def MOIS(col: pl.Expr) -> pl.Expr:
        return col.dt.month()  # noqa: N802

    def JOUR(col: pl.Expr) -> pl.Expr:
        return col.dt.day()  # noqa: N802

    def AUJOURD_HUI() -> pl.Expr:
        return pl.lit(datetime.date.today())  # noqa: N802

    def SI(
        cond: pl.Expr,
        alors: pl.Expr | str | int | float,  # noqa: N802
        sinon: pl.Expr | str | int | float,
    ) -> pl.Expr:
        alors_ = pl.lit(alors) if not isinstance(alors, pl.Expr) else alors
        sinon_ = pl.lit(sinon) if not isinstance(sinon, pl.Expr) else sinon
        return pl.when(cond).then(alors_).otherwise(sinon_)

    namespace: dict = {
        # Functions
        "CONCATENER": CONCATENER,
        "MAJUSCULE": MAJUSCULE,
        "MINUSCULE": MINUSCULE,
        "GAUCHE": GAUCHE,
        "DROITE": DROITE,
        "NBCAR": NBCAR,
        "SUPPRESPACE": SUPPRESPACE,
        "ARRONDI": ARRONDI,
        "ABS": ABS,
        "MULTIPLIER": MULTIPLIER,
        "AJOUTER": AJOUTER,
        "ANNEE": ANNEE,
        "MOIS": MOIS,
        "JOUR": JOUR,
        "AUJOURD_HUI": AUJOURD_HUI,
        "SI": SI,
        # Column helper
        "col": pl.col,
    }

    # Direct column references: prenom → pl.col("prenom")
    for col_name in df.columns:
        namespace.setdefault(col_name, pl.col(col_name))

    return namespace


# Allowed identifier names (updated at eval time from namespace keys)
_STATIC_ALLOWED = {
    "CONCATENER",
    "MAJUSCULE",
    "MINUSCULE",
    "GAUCHE",
    "DROITE",
    "NBCAR",
    "SUPPRESPACE",
    "ARRONDI",
    "ABS",
    "MULTIPLIER",
    "AJOUTER",
    "ANNEE",
    "MOIS",
    "JOUR",
    "AUJOURD_HUI",
    "SI",
    "col",
}

# Public catalog for the JS layer (same order as UI display)
FUNCTION_CATALOG: list[dict] = [
    {
        "name": "CONCATENER",
        "label": "CONCATENER",
        "cat": "Texte",
        "hint": "CONCATENER(col1, col2, …)",
    },
    {
        "name": "MAJUSCULE",
        "label": "MAJUSCULE",
        "cat": "Texte",
        "hint": "MAJUSCULE(col)",
    },
    {
        "name": "MINUSCULE",
        "label": "MINUSCULE",
        "cat": "Texte",
        "hint": "MINUSCULE(col)",
    },
    {"name": "GAUCHE", "label": "GAUCHE", "cat": "Texte", "hint": "GAUCHE(col, n)"},
    {"name": "DROITE", "label": "DROITE", "cat": "Texte", "hint": "DROITE(col, n)"},
    {"name": "NBCAR", "label": "NBCAR", "cat": "Texte", "hint": "NBCAR(col)"},
    {
        "name": "SUPPRESPACE",
        "label": "SUPPRESPACE",
        "cat": "Texte",
        "hint": "SUPPRESPACE(col)",
    },
    {"name": "ARRONDI", "label": "ARRONDI", "cat": "Math", "hint": "ARRONDI(col, n)"},
    {"name": "ABS", "label": "ABS", "cat": "Math", "hint": "ABS(col)"},
    {
        "name": "MULTIPLIER",
        "label": "MULTIPLIER",
        "cat": "Math",
        "hint": "MULTIPLIER(col, n)",
    },
    {
        "name": "AJOUTER",
        "label": "AJOUTER",
        "cat": "Math",
        "hint": "AJOUTER(col1, col2)",
    },
    {"name": "ANNEE", "label": "ANNEE", "cat": "Date", "hint": "ANNEE(col)"},
    {"name": "MOIS", "label": "MOIS", "cat": "Date", "hint": "MOIS(col)"},
    {"name": "JOUR", "label": "JOUR", "cat": "Date", "hint": "JOUR(col)"},
    {
        "name": "AUJOURD_HUI",
        "label": "AUJOURD'HUI",
        "cat": "Date",
        "hint": "AUJOURD_HUI()",
    },
    {"name": "SI", "label": "SI", "cat": "Logique", "hint": "SI(cond, alors, sinon)"},
]


# ///////////////////////////////////////////////////////////////
# AST VALIDATOR
# ///////////////////////////////////////////////////////////////


class _SafeVisitor(ast.NodeVisitor):
    _ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.Call,
        ast.Name,
        ast.Constant,
        ast.Attribute,
        ast.Subscript,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Set,
        ast.Load,
        ast.keyword,
        ast.IfExp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.MatMult,
        ast.UAdd,
        ast.USub,
        ast.Invert,
        ast.Not,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,
        ast.BitOr,
        ast.BitAnd,
        ast.BitXor,
        ast.LShift,
        ast.RShift,
    )

    def __init__(self, allowed: set[str]) -> None:
        self.allowed = allowed

    def visit(self, node: ast.AST) -> None:  # type: ignore[override]
        if not isinstance(node, self._ALLOWED_NODES):
            raise ValueError(
                f"Disallowed expression element: {node.__class__.__name__}"
            )
        super().visit(node)

    def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
        if node.id not in self.allowed:
            raise NameError(
                f"'{node.id}' is not available. Use column names or catalog functions."
            )

    def visit_Attribute(self, node: ast.Attribute) -> None:  # type: ignore[override]
        if node.attr.startswith("_"):
            raise ValueError(f"Access to '{node.attr}' is forbidden")
        self.visit(node.value)

    def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            raise ValueError("Only named function calls are allowed")
        for kw in node.keywords:
            if kw.arg and kw.arg.startswith("_"):
                raise ValueError(f"Keyword '{kw.arg}' is forbidden")
        self.generic_visit(node)


# ///////////////////////////////////////////////////////////////
# BRACKET SYNTAX — [Column Name] for non-identifier column names
# ///////////////////////////////////////////////////////////////

_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")


def _desugar_bracket_columns(
    expression: str, columns: list[str]
) -> tuple[str, dict[str, str]]:
    """Replace ``[Column Name]`` references with safe placeholder identifiers.

    Column names containing spaces, leading digits, or symbols (°, €, -, …)
    aren't valid Python identifiers and can't be referenced bare in the
    expression AST. The ``[Column Name]`` syntax lets users quote them
    explicitly. Only brackets whose content matches a known column name are
    replaced, so plain list literals (e.g. ``[1, 2, 3]``) are left untouched.
    """
    aliases: dict[str, str] = {}

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in columns:
            return match.group(0)
        alias = aliases.setdefault(name, f"_col_{len(aliases)}")
        return alias

    return _BRACKET_RE.sub(_replace, expression), aliases


# ///////////////////////////////////////////////////////////////
# STEP FUNCTION
# ///////////////////////////////////////////////////////////////


@action("add_computed_column")
def add_computed_column(
    df: pl.DataFrame,
    target: str,
    expression: str,
) -> pl.DataFrame:
    """Add a computed column using an Excel-style expression.

    Available functions: CONCATENER, MAJUSCULE, MINUSCULE, GAUCHE, DROITE,
    NBCAR, SUPPRESPACE, ARRONDI, ABS, MULTIPLIER, AJOUTER, ANNEE, MOIS,
    JOUR, AUJOURD_HUI, SI. Column names are accessible directly by name, or
    wrapped in brackets (``[Column Name]``) when they aren't valid Python
    identifiers (spaces, leading digits, symbols…).

    Example:
        >>> df = pl.DataFrame({"prenom": ["Alice"], "nom": ["Smith"]})
        >>> add_computed_column(df, "complet", 'MAJUSCULE(CONCATENER(prenom, " ", nom))')
        shape: (1, 3)
    """
    expression, bracket_aliases = _desugar_bracket_columns(expression, df.columns)
    namespace = _make_namespace(df)
    for col_name, alias in bracket_aliases.items():
        namespace[alias] = pl.col(col_name)
    allowed_names = _STATIC_ALLOWED | set(df.columns) | set(bracket_aliases.values())

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid syntax: {exc}") from exc

    try:
        _SafeVisitor(allowed_names).visit(parsed)
    except Exception as exc:
        raise ValueError(f"Expression not allowed: {exc}") from exc

    try:
        code_obj = compile(parsed, "<computed>", "eval")
        # eval() is safe here: the AST is fully validated by _SafeVisitor before
        # reaching this point (whitelist of node types + allowed names), builtins
        # are stripped, and the namespace contains only Polars wrappers + column refs.
        expr = eval(code_obj, {"__builtins__": {}}, namespace)  # noqa: S307  # nosec B307
    except Exception as exc:
        raise ValueError(f"Evaluation error: {exc}") from exc

    if not isinstance(expr, pl.Expr):
        raise TypeError(
            f"The expression must return a Polars Expr, got: {type(expr).__name__}"
        )

    return df.with_columns(expr.alias(target))


__all__ = ["add_computed_column", "FUNCTION_CATALOG"]
