import duckdb
import pandas as pd
from datakit.data import load_table

customers = load_table("customers")
orders = load_table("orders")


def inactivos_por_segmento(customers: pd.DataFrame, orders: pd.DataFrame, desde: str) -> pd.DataFrame:
    """Columnas: segment, clientes, inactivos, pct_inactivos."""
    con = duckdb.connect()
    con.register("customers", customers)
    con.register("orders", orders)
    sql = """
        WITH base AS (
            SELECT c.customer_id, c.segment
            FROM customers AS c
            WHERE c.signup_date < CAST(? AS DATE)
        ),
        activos AS (
            SELECT DISTINCT customer_id
            FROM orders
            WHERE status <> 'cancelado' AND order_date >= CAST(? AS DATE)
        )
        SELECT b.segment,
               COUNT(*) AS clientes,
               COUNT(*) FILTER (WHERE a.customer_id IS NULL) AS inactivos,
               ROUND(100.0 * COUNT(*) FILTER (WHERE a.customer_id IS NULL) / COUNT(*), 1) AS pct_inactivos
        FROM base AS b
        LEFT JOIN activos AS a USING (customer_id)
        GROUP BY b.segment
        ORDER BY b.segment
    """
    return con.execute(sql, [desde, desde]).df()


print(inactivos_por_segmento(customers, orders, "2026-01-01"))
