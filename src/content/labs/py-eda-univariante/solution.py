import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")

no_canceladas = orders[orders["status"] != "cancelado"]
por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
importes = por_pedido.reindex(no_canceladas["order_id"]).reset_index(drop=True)
gasto_por_cliente = (
    por_pedido.reindex(no_canceladas["order_id"]).groupby(no_canceladas["customer_id"].to_numpy()).sum()
)
fechas_2025 = no_canceladas.loc[no_canceladas["order_date"].dt.year == 2025, "order_date"]
print(len(importes), len(gasto_por_cliente), len(fechas_2025))


def resumen_numerico(x: pd.Series) -> dict:
    """n, media, mediana, p10, p90, p99 (1 decimal) y asimetria (2 decimales)."""
    return {
        "n": int(x.notna().sum()),
        "media": round(float(x.mean()), 1),
        "mediana": round(float(x.median()), 1),
        "p10": round(float(x.quantile(0.10)), 1),
        "p90": round(float(x.quantile(0.90)), 1),
        "p99": round(float(x.quantile(0.99)), 1),
        "asimetria": round(float(x.skew()), 2),
    }


def concentracion_pareto(x: pd.Series, fracciones=(0.01, 0.10, 0.20)) -> dict:
    """{fraccion: % del total (1 decimal) que suman esa fracción de mayores valores}."""
    ordenado = x.sort_values(ascending=False)
    total = ordenado.sum()
    return {f: round(float(ordenado.head(int(len(ordenado) * f)).sum() / total * 100), 1) for f in fracciones}


def pedidos_por_dia_semana(fechas: pd.Series) -> pd.Series:
    """Media de pedidos por día, para cada día de la semana (índice 0=lunes ... 6=domingo)."""
    dia = fechas.dt.dayofweek
    pedidos = dia.value_counts().sort_index()
    dias_distintos = fechas.dt.normalize().drop_duplicates().dt.dayofweek.value_counts().sort_index()
    return (pedidos / dias_distintos).round(0).astype(int)


print(resumen_numerico(importes))
print(concentracion_pareto(gasto_por_cliente))
print(pedidos_por_dia_semana(fechas_2025))
