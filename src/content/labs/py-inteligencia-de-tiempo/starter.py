import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")

por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
ok = orders[orders["status"] != "cancelado"]
mensual = (
    por_pedido.reindex(ok["order_id"])
    .groupby(ok["order_date"].dt.to_period("M").dt.to_timestamp().to_numpy())
    .sum()
    .rename("ingresos")
    .rename_axis("mes")
    .reset_index()
)
print(mensual.tail(3))


def completar_meses(df: pd.DataFrame) -> pd.DataFrame:
    """Todos los meses entre el primero y el último; los ausentes con ingresos = 0."""
    # TODO
    ...


def con_comparaciones(df: pd.DataFrame) -> pd.DataFrame:
    """mes, ingresos, ytd, py, yoy_pct (1 decimal) y movil_12m sobre la serie completa."""
    # TODO
    ...


def ytd_hasta(df: pd.DataFrame, anio: int, mes: int) -> float:
    """Acumulado del año hasta ese mes."""
    # TODO
    ...


# Cuando estén listas: compara el YTD de junio de 2026 con el de junio de 2025.
# print(ytd_hasta(mensual, 2026, 6), ytd_hasta(mensual, 2025, 6))
