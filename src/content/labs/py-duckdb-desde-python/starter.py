import duckdb
import pandas as pd
from datakit.data import load_table

customers = load_table("customers")
orders = load_table("orders")


def inactivos_por_segmento(customers: pd.DataFrame, orders: pd.DataFrame, desde: str) -> pd.DataFrame:
    """Columnas: segment, clientes, inactivos, pct_inactivos."""
    # TODO: conexión de DuckDB, register de los DataFrames, SQL con un parámetro `?` para `desde`.
    ...


print(inactivos_por_segmento(customers, orders, "2026-01-01"))
