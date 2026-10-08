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
    # TODO
    ...


r = descomponer_pvm(g2024, g2025)
print({k: round(v) for k, v in r.items()})
