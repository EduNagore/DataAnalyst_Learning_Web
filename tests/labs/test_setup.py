"""Placeholder hasta la Fase 4 (laboratorios).

Comprueba que el entorno Python del proyecto arranca con las versiones
fijadas en pyproject.toml, alineadas con lo que trae Pyodide (PLAN.md §8).
Los tests reales de laboratorios SQL/Python (test_sql_labs.py,
test_py_labs.py) se añaden en la Fase 4.
"""

import duckdb
import pandas as pd
import polars as pl


def test_pandas_disponible():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert df["a"].sum() == 6


def test_polars_disponible():
    df = pl.DataFrame({"a": [1, 2, 3]})
    assert df["a"].sum() == 6


def test_duckdb_disponible():
    result = duckdb.sql("SELECT sum(x) AS total FROM (VALUES (1), (2), (3)) AS t(x)").fetchone()
    assert result[0] == 6
