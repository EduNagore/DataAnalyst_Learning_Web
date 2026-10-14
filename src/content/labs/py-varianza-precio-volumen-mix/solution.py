import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
products = load_table("products")
categories = load_table("categories")


def ventas_por_categoria(orders, order_items, products, desde: str, hasta: str) -> pd.DataFrame:
    """Unidades, ingresos y precio medio por categoría principal (los 6 primeros caracteres de `category_id`,
    p. ej. «cat-00») en pedidos no cancelados entre `desde` y `hasta` (ambos incluidos)."""
    o = orders.loc[
        (orders["status"] != "cancelado") & (orders["order_date"] >= desde) & (orders["order_date"] <= hasta),
        ["order_id"],
    ]
    x = order_items.merge(o, on="order_id").merge(products[["product_id", "category_id"]], on="product_id")
    x["categoria"] = x["category_id"].str[:6]
    x["ingresos"] = x["quantity"] * x["unit_price"]
    t = x.groupby("categoria").agg(unidades=("quantity", "sum"), ingresos=("ingresos", "sum"))
    t["precio_medio"] = t["ingresos"] / t["unidades"]
    return t


def descomponer(base: pd.DataFrame, actual: pd.DataFrame) -> dict:
    """Puente de ingresos entre dos periodos con las mismas categorías:
    precio = Σ (p1 − p0)·q1; volumen = (Q1 − Q0)·(R0/Q0); mix = Σ p0·q1 − R0·Q1/Q0.
    Devuelve variacion, precio, volumen y mix (precio + volumen + mix = variación)."""
    q0, q1 = base["unidades"], actual["unidades"]
    p0, p1 = base["precio_medio"], actual["precio_medio"]
    r0 = float(base["ingresos"].sum())
    precio = float(((p1 - p0) * q1).sum())
    volumen = float((q1.sum() - q0.sum()) * r0 / q0.sum())
    mix = float((p0 * q1).sum() - r0 * q1.sum() / q0.sum())
    return {"variacion": float(actual["ingresos"].sum() - r0), "precio": precio, "volumen": volumen, "mix": mix}


def mix_por_categoria(base: pd.DataFrame, actual: pd.DataFrame) -> pd.Series:
    """Contribución de cada categoría al efecto mix: (q1 − cuota0·Q1)·p0."""
    cuota0 = base["unidades"] / base["unidades"].sum()
    return (actual["unidades"] - cuota0 * actual["unidades"].sum()) * base["precio_medio"]


h1_25 = ventas_por_categoria(orders, order_items, products, "2025-01-01", "2025-06-30")
h1_26 = ventas_por_categoria(orders, order_items, products, "2026-01-01", "2026-06-30")
puente = descomponer(h1_25, h1_26)
print({k: round(v / 1e6, 2) for k, v in puente.items()})
print((mix_por_categoria(h1_25, h1_26) / 1e6).round(2).to_dict())
