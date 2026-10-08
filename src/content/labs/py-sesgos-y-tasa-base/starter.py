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
    # TODO
    ...


def regresion_a_la_media(h1: pd.Series, h2: pd.Series, q: float = 0.9) -> dict:
    """n, h1_medio, h2_medio (0 dec.), ratio (2 dec.) y correlacion (3 dec.)."""
    # TODO
    ...


def precision_alerta(sensibilidad: float, especificidad: float, tasa_base: float) -> dict:
    """precision_pct (1 decimal) y falsos_por_verdadero (2 decimales)."""
    # TODO
    ...


print(valor_por_cliente(cohortes))
print(regresion_a_la_media(h1, h2))
print(precision_alerta(0.80, 0.90, 0.0626))
