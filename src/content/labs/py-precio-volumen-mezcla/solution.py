import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")
products = load_table("products")
categories = load_table("categories").set_index("category_id")

# Categoría de nivel superior de cada producto.
padre = categories["parent_category_id"].fillna(categories.index.to_series())
nombre_cat = padre.map(categories["name"])
productos = products.assign(cat=products["category_id"].map(nombre_cat))[["product_id", "cat"]]

lineas = (
    items.merge(orders[["order_id", "order_date", "status"]], on="order_id")
    .query("status != 'cancelado'")
    .merge(productos, on="product_id")
    .assign(anio=lambda d: d["order_date"].dt.year, r=lambda d: d["quantity"] * d["unit_price"])
)
g2024 = lineas[lineas["anio"] == 2024].groupby("cat").agg(q=("quantity", "sum"), r=("r", "sum"))
g2025 = lineas[lineas["anio"] == 2025].groupby("cat").agg(q=("quantity", "sum"), r=("r", "sum"))
print(g2024.round(0))


def descomponer_pvm(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """volumen, mezcla, precio y total (variación de ingresos) entre a (base) y b (comparado)."""
    cats = a.index.union(b.index)
    a = a.reindex(cats).fillna(0.0)
    b = b.reindex(cats).fillna(0.0)
    q0, q1 = a["q"].sum(), b["q"].sum()
    s0, s1 = a["q"] / q0, b["q"] / q1
    p0 = (a["r"] / a["q"]).where(a["q"] > 0, 0.0)
    p1 = (b["r"] / b["q"]).where(b["q"] > 0, 0.0)
    return {
        "volumen": float((q1 - q0) * (s0 * p0).sum()),
        "mezcla": float(q1 * ((s1 - s0) * p0).sum()),
        "precio": float(q1 * (s1 * (p1 - p0)).sum()),
        "total": float(b["r"].sum() - a["r"].sum()),
    }


r = descomponer_pvm(g2024, g2025)
print({k: round(v) for k, v in r.items()})
