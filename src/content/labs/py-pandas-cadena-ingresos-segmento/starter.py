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
    # TODO: une order_items -> orders -> customers (validate="many_to_one"),
    # filtra año y estado, calcula ingresos y agrega por segmento.
    ...


print(ingresos_por_segmento(orders, order_items, customers, 2025))
