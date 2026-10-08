import polars as pl
from datakit.data import load_table

orders = pl.from_pandas(load_table("orders")).lazy()
order_items = pl.from_pandas(load_table("order_items")).lazy()


def ingresos_mensuales(orders: pl.LazyFrame, order_items: pl.LazyFrame, anio: int) -> pl.LazyFrame:
    """Columnas: mes, ingresos, crec_pct. Sin pedidos cancelados, ordenado por mes."""
    # TODO: une order_items con orders (validate="m:1"), filtra estado y año,
    # agrupa por mes, suma quantity * unit_price y calcula pct_change.
    ...


print(ingresos_mensuales(orders, order_items, 2025).collect())
