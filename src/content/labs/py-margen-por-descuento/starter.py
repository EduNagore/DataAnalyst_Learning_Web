import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
products = load_table("products")


def margen_por_descuento(orders: pd.DataFrame, order_items: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """discount_pct, pedidos, margen_pct y margen_por_pedido (1 decimal), por nivel de descuento."""
    # TODO: margen e ingresos por pedido (con el coste de products), filtra cancelados y agrupa.
    ...


def ratio_margen_goodhart(tabla: pd.DataFrame) -> float:
    """Margen por pedido con el descuento máximo / margen por pedido sin descuento (2 decimales)."""
    # TODO
    ...


tabla = margen_por_descuento(orders, order_items, products)
print(tabla)
print(ratio_margen_goodhart(tabla))
