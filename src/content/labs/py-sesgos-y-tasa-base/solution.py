import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")
customers = load_table("customers")

por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
ok = orders[orders["status"] != "cancelado"].assign(total=lambda d: d["order_id"].map(por_pedido))

gasto_2025 = ok[ok["order_date"].dt.year == 2025].groupby("customer_id")["total"].sum()
cohortes = customers.assign(anio=customers["signup_date"].dt.year)
cohortes = cohortes[cohortes["anio"] <= 2024][["customer_id", "anio"]].copy()
cohortes["gasto"] = cohortes["customer_id"].map(gasto_2025).fillna(0.0)
cohortes["activo"] = cohortes["gasto"] > 0

s1 = ok[(ok["order_date"] >= "2025-01-01") & (ok["order_date"] < "2025-07-01")].groupby("customer_id")["total"].sum()
s2 = ok[(ok["order_date"] >= "2025-07-01") & (ok["order_date"] < "2026-01-01")].groupby("customer_id")["total"].sum()
h1 = s1
h2 = s2.reindex(h1.index).fillna(0.0)
print(len(cohortes), len(h1))


def valor_por_cliente(cohortes: pd.DataFrame) -> pd.DataFrame:
    """anio, clientes, activos, gasto_por_activo, gasto_por_captado (0 decimales), por año."""
    g = cohortes.groupby("anio").agg(
        clientes=("customer_id", "size"), activos=("activo", "sum"), gasto=("gasto", "sum")
    )
    g["activos"] = g["activos"].astype(int)
    g["gasto_por_activo"] = (g["gasto"] / g["activos"]).round(0)
    g["gasto_por_captado"] = (g["gasto"] / g["clientes"]).round(0)
    return g.drop(columns="gasto").reset_index().sort_values("anio").reset_index(drop=True)


def regresion_a_la_media(h1: pd.Series, h2: pd.Series, q: float = 0.9) -> dict:
    """n, h1_medio, h2_medio (0 dec.), ratio (2 dec.) y correlacion (3 dec.)."""
    top = h1 >= h1.quantile(q)
    h1_medio, h2_medio = h1[top].mean(), h2[top].mean()
    return {
        "n": int(top.sum()),
        "h1_medio": round(float(h1_medio), 0),
        "h2_medio": round(float(h2_medio), 0),
        "ratio": round(float(h2_medio / h1_medio), 2),
        "correlacion": round(float(h1.corr(h2)), 3),
    }


def precision_alerta(sensibilidad: float, especificidad: float, tasa_base: float) -> dict:
    """precision_pct (1 decimal) y falsos_por_verdadero (2 decimales)."""
    verdaderos = sensibilidad * tasa_base
    falsos = (1 - especificidad) * (1 - tasa_base)
    return {
        "precision_pct": round(verdaderos / (verdaderos + falsos) * 100, 1),
        "falsos_por_verdadero": round(falsos / verdaderos, 2),
    }


print(valor_por_cliente(cohortes))
print(regresion_a_la_media(h1, h2))
print(precision_alerta(0.80, 0.90, 0.0626))
