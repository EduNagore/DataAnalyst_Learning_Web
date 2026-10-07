"""Aserciones con mensajes didácticos en español para los tests de los labs."""

import math

import pandas as pd


def assert_close(actual, expected, tol: float = 1e-6, label: str = "El valor") -> None:
    """Compara dos números con tolerancia absoluta."""
    try:
        ok = math.isclose(float(actual), float(expected), abs_tol=tol, rel_tol=0)
    except (TypeError, ValueError):
        raise AssertionError(f"{label} no es un número: {actual!r}.") from None
    if not ok:
        raise AssertionError(f"{label} debería ser {expected}, pero es {actual}.")


def assert_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """Comprueba que el DataFrame tiene (al menos) estas columnas."""
    if not isinstance(df, pd.DataFrame):
        raise AssertionError(f"Se esperaba un DataFrame y se recibió {type(df).__name__}.")
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise AssertionError(
            f"Faltan columnas: {', '.join(missing)}. Tu resultado tiene: {', '.join(map(str, df.columns))}."
        )


def assert_frame_equivalent(
    actual: pd.DataFrame,
    expected: pd.DataFrame,
    sort_by: list[str] | None = None,
    tol: float = 1e-6,
) -> None:
    """Compara dos DataFrames ignorando el orden de filas (si se da `sort_by`) y con tolerancia en floats."""
    assert_columns(actual, list(expected.columns))
    a = actual[list(expected.columns)].reset_index(drop=True)
    e = expected.reset_index(drop=True)
    if sort_by:
        a = a.sort_values(sort_by).reset_index(drop=True)
        e = e.sort_values(sort_by).reset_index(drop=True)
    if len(a) != len(e):
        word = "sobran" if len(a) > len(e) else "faltan"
        raise AssertionError(
            f"Tu resultado tiene {len(a)} filas y se esperaban {len(e)} ({word} {abs(len(a) - len(e))})."
        )
    for col in e.columns:
        for i, (x, y) in enumerate(zip(a[col], e[col], strict=True)):
            if isinstance(y, float) or isinstance(x, float):
                if pd.isna(x) and pd.isna(y):
                    continue
                if pd.isna(x) or pd.isna(y) or abs(float(x) - float(y)) > tol:
                    raise AssertionError(f"Columna «{col}», fila {i + 1}: esperado {y}, obtenido {x}.")
            elif x != y and not (pd.isna(x) and pd.isna(y)):
                raise AssertionError(f"Columna «{col}», fila {i + 1}: esperado {y!r}, obtenido {x!r}.")
