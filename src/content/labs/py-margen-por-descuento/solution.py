import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
products = load_table("products")


def margen_por_descuento(orders: pd.DataFrame, order_items: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """discount_pct, pedidos, margen_pct y margen_por_pedido (1 decimal), por nivel de descuento."""
    lineas = order_items.merge(products[["product_id", "cost"]], on="product_id", validate="many_to_one").assign(
        ingresos=lambda d: d["quantity"] * d["unit_price"],
        margen=lambda d: d["quantity"] * (d["unit_price"] - d["cost"]),
    )
    por_pedido = lineas.groupby("order_id")[["ingresos", "margen"]].sum()
    ok = orders[orders["status"] != "cancelado"][["order_id", "discount_pct"]].join(por_pedido, on="order_id")
    g = ok.groupby("discount_pct").agg(pedidos=("order_id", "size"), ingresos=("ingresos", "sum"), margen=("margen", "sum"))
    g["margen_pct"] = (100 * g["margen"] / g["ingresos"]).round(1)
    g["margen_por_pedido"] = (g["margen"] / g["pedidos"]).round(1)
    return g.reset_index()[["discount_pct", "pedidos", "margen_pct", "margen_por_pedido"]].sort_values("discount_pct").reset_index(drop=True)


def ratio_margen_goodhart(tabla: pd.DataFrame) -> float:
    """Margen por pedido con el descuento máximo / margen por pedido sin descuento (2 decimales)."""
    t = tabla.set_index("discount_pct")["margen_por_pedido"]
    return round(float(t.loc[t.index.max()] / t.loc[0.0]), 2)


tabla = margen_por_descuento(orders, order_items, products)
print(tabla)
print(ratio_margen_goodhart(tabla))
