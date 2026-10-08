import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
print(orders.shape, order_items.shape, customers.shape)


def ingresos_por_segmento(
    orders: pd.DataFrame, order_items: pd.DataFrame, customers: pd.DataFrame, anio: int
) -> pd.DataFrame:
    """Columnas: segment, pedidos, ingresos, ticket_medio. Sin pedidos cancelados."""
    return (
        order_items.merge(
            orders[["order_id", "customer_id", "order_date", "status"]],
            on="order_id",
            validate="many_to_one",
        )
        .merge(customers[["customer_id", "segment"]], on="customer_id", validate="many_to_one")
        .loc[lambda d: (d["status"] != "cancelado") & (d["order_date"].dt.year == anio)]
        .assign(ingresos=lambda d: d["quantity"] * d["unit_price"])
        .groupby("segment", as_index=False)
        .agg(pedidos=("order_id", "nunique"), ingresos=("ingresos", "sum"))
        .assign(ticket_medio=lambda d: (d["ingresos"] / d["pedidos"]).round(2))
    )


print(ingresos_por_segmento(orders, order_items, customers, 2025))
