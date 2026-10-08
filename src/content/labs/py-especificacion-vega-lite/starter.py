import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")
products = load_table("products")
categories = load_table("categories").set_index("category_id")

padre = categories["parent_category_id"].fillna(categories.index.to_series())
nombre_cat = padre.map(categories["name"])
lineas = (
    items.merge(orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == 2025)][["order_id"]], on="order_id")
    .merge(products[["product_id", "category_id"]], on="product_id")
    .assign(categoria=lambda d: d["category_id"].map(nombre_cat))
)
unidades = lineas.groupby("categoria")["quantity"].sum()
cuotas = (unidades / unidades.sum() * 100).round(1).rename("pct").reset_index()
print(cuotas.sort_values("pct", ascending=False).to_string(index=False))


def espec_barras_ordenadas(df: pd.DataFrame, categoria: str, valor: str, titulo: str) -> dict:
    """Especificación Vega-Lite de barras horizontales ordenadas, con el eje en cero."""
    # TODO
    ...


def elegir_grafico(intencion: str, n_categorias: int = 0) -> str:
    """Gráfico recomendado según la intención (ver tabla del enunciado)."""
    # TODO
    ...


espec = espec_barras_ordenadas(cuotas, "categoria", "pct", "Alimentación vende más (13,5 %) y Moda menos (11,6 %)")
print(espec)
print(elegir_grafico("comparar", 8), "|", elegir_grafico("composicion", 3))
