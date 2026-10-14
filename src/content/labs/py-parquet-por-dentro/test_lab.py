import io

import pandas as pd
import pyarrow.parquet as pq
from datakit.data import load_table


def _ord(ns):
    return load_table("orders").sort_values("order_date").reset_index(drop=True)


def test_csv_frente_a_parquet(ns):
    """El mismo DataFrame ocupa ≈ 29 MB en CSV y ≈ 3,7 MB en Parquet con zstd (7,7 veces menos)"""
    df = _ord(ns)
    csv, par = ns["a_csv"](df), ns["a_parquet"](df)
    assert 27e6 < len(csv) < 31e6
    assert len(csv) / len(par) > 6
    md = pq.ParquetFile(io.BytesIO(par)).metadata
    assert md.num_rows == len(df) and md.num_row_groups == 8


def test_bytes_por_columna(ns):
    """La columna order_id (identificadores únicos) es la más pesada y las columnas suman casi todo el fichero"""
    par = ns["a_parquet"](_ord(ns))
    b = ns["bytes_por_columna"](par)
    assert b.index[0] == "order_id" and b.is_monotonic_decreasing
    assert 0.9 < b.sum() / len(par) <= 1.0
    assert b["channel"] < b["order_id"] / 20, "Una columna con pocos valores distintos casi no pesa."


def test_poda_de_grupos_de_filas(ns):
    """Marzo de 2026: con los datos ordenados por fecha solo 1 de 8 grupos; ordenados por cliente, los 8"""
    df = load_table("orders")
    ordenado = ns["a_parquet"](df.sort_values("order_date").reset_index(drop=True))
    desordenado = ns["a_parquet"](df.sort_values("customer_id").reset_index(drop=True))
    assert len(ns["grupos_a_leer"](ordenado, "order_date", "2026-03-01", "2026-03-31")) == 1
    assert len(ns["grupos_a_leer"](desordenado, "order_date", "2026-03-01", "2026-03-31")) == 8
    g = ns["grupos_a_leer"](ordenado, "order_date", "2026-03-01", "2026-03-31")
    assert ns["fraccion_leida"](ordenado, ["order_date", "status"], g) < 0.01
    assert abs(ns["fraccion_leida"](ordenado, list(df.columns), list(range(8))) - 1) < 1e-9


def test_hidden_fichero_pequeno(ns):
    """Tres grupos de dos filas con estadísticas conocidas (test oculto)"""
    df = pd.DataFrame(
        {
            "dia": pd.to_datetime(["2025-01-01", "2025-01-05", "2025-02-01", "2025-02-09", "2025-03-01", "2025-03-04"]),
            "importe": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        }
    )
    par = ns["a_parquet"](df, filas_por_grupo=2, compresion="snappy")
    assert ns["grupos_a_leer"](par, "dia", "2025-02-05", "2025-02-20") == [1]
    assert ns["grupos_a_leer"](par, "dia", "2025-01-05", "2025-02-01") == [0, 1]
    assert ns["grupos_a_leer"](par, "dia", "2026-01-01", "2026-12-31") == []
    f = ns["fraccion_leida"](par, ["dia"], [1])
    todos = ns["fraccion_leida"](par, ["dia", "importe"], [0, 1, 2])
    assert 0 < f < 1 and abs(todos - 1) < 1e-9
    assert len(ns["a_csv"](df).decode().splitlines()) == 7
