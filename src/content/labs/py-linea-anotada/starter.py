import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")

por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
ok = orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == 2025)]
mensual = (
    por_pedido.reindex(ok["order_id"])
    .groupby(ok["order_date"].dt.to_period("M").dt.to_timestamp().to_numpy())
    .sum()
    .div(1e6)
    .round(2)
    .rename("m")
    .rename_axis("mes")
    .reset_index()
    .assign(mes=lambda d: d["mes"].dt.strftime("%Y-%m-%d"))
)
print(mensual.to_string(index=False))


def espec_linea_anotada(
    df: pd.DataFrame, x: str, y: str, titulo: str, x_anotacion: str, texto: str, unidad: str
) -> dict:
    """Vega-Lite v6 con tres capas: línea, regla vertical en x_anotacion y texto."""
    # TODO
    ...


espec = espec_linea_anotada(
    mensual, "mes", "m", "Los ingresos netos casi se duplican en 2025", "2025-03-01",
    "Fin de las rebajas: +22,6 % sobre febrero", "M€",
)
print(espec["title"], [c.get("mark") for c in espec["layer"]])
