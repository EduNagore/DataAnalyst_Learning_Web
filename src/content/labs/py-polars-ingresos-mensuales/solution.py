import polars as pl
from datakit.data import load_table

orders = pl.from_pandas(load_table("orders")).lazy()
order_items = pl.from_pandas(load_table("order_items")).lazy()


def ingresos_mensuales(orders: pl.LazyFrame, order_items: pl.LazyFrame, anio: int) -> pl.LazyFrame:
    """Columnas: mes, ingresos, crec_pct. Sin pedidos cancelados, ordenado por mes."""
    return (
        order_items.join(orders.select("order_id", "order_date", "status"), on="order_id", validate="m:1")
        .filter(pl.col("status") != "cancelado", pl.col("order_date").dt.year() == anio)
        .group_by(pl.col("order_date").dt.month().alias("mes"))
        .agg((pl.col("quantity") * pl.col("unit_price")).sum().alias("ingresos"))
        .sort("mes")
        .with_columns((pl.col("ingresos").pct_change() * 100).round(1).alias("crec_pct"))
    )


print(ingresos_mensuales(orders, order_items, 2025).collect())
