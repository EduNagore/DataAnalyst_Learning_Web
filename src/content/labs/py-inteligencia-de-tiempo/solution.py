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
    serie = df.set_index("mes")["ingresos"].sort_index()
    meses = pd.date_range(serie.index.min(), serie.index.max(), freq="MS")
    return serie.reindex(meses, fill_value=0.0).rename("ingresos").rename_axis("mes").reset_index()


def con_comparaciones(df: pd.DataFrame) -> pd.DataFrame:
    """mes, ingresos, ytd, py, yoy_pct (1 decimal) y movil_12m sobre la serie completa."""
    c = completar_meses(df)
    c["ytd"] = c.groupby(c["mes"].dt.year)["ingresos"].cumsum()
    c["py"] = c["ingresos"].shift(12)
    c["yoy_pct"] = ((c["ingresos"] / c["py"] - 1) * 100).round(1)
    c["movil_12m"] = c["ingresos"].rolling(12).sum()
    return c


def ytd_hasta(df: pd.DataFrame, anio: int, mes: int) -> float:
    """Acumulado del año hasta ese mes."""
    c = con_comparaciones(df)
    fila = c[(c["mes"].dt.year == anio) & (c["mes"].dt.month == mes)]
    return float(fila["ytd"].iloc[0])


print(round(ytd_hasta(mensual, 2026, 6)), round(ytd_hasta(mensual, 2025, 6)))
