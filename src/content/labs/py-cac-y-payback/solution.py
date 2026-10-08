import pandas as pd
from datakit.data import load_table

marketing_spend = load_table("marketing_spend")
customers = load_table("customers")
orders = load_table("orders")
order_items = load_table("order_items")
products = load_table("products")

# Margen de contribución por cliente y mes desde el alta, para la cohorte de 2024 (ya calculado).
lineas = order_items.merge(products[["product_id", "cost"]], on="product_id").assign(
    margen=lambda d: d["quantity"] * (d["unit_price"] - d["cost"])
)
por_pedido = lineas.groupby("order_id")["margen"].sum()
cohorte = customers[customers["signup_date"].dt.year == 2024].assign(
    mes_alta=lambda d: d["signup_date"].dt.to_period("M")
)
ped = orders[orders["status"] != "cancelado"].merge(cohorte[["customer_id", "mes_alta"]], on="customer_id")
ped = ped.assign(margen=ped["order_id"].map(por_pedido), mes_pedido=ped["order_date"].dt.to_period("M"))
ped = ped.assign(mes=(ped["mes_pedido"] - ped["mes_alta"]).apply(lambda x: x.n))
margen_mensual = ped[ped["mes"].between(0, 12)].groupby("mes")["margen"].sum() / len(cohorte)
print(margen_mensual.round(1).to_dict())


def cac_por_anio(marketing_spend: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """anio, gasto (0 dec.), clientes_nuevos y cac_mixto (2 dec.), por año."""
    gasto = marketing_spend.groupby(marketing_spend["date"].dt.year)["spend_eur"].sum().rename("gasto")
    altas = customers.groupby(customers["signup_date"].dt.year).size().rename("clientes_nuevos")
    t = pd.concat([gasto, altas], axis=1).dropna().rename_axis("anio").reset_index()
    t["clientes_nuevos"] = t["clientes_nuevos"].astype(int)
    t["cac_mixto"] = (t["gasto"] / t["clientes_nuevos"]).round(2)
    t["gasto"] = t["gasto"].round(0)
    return t.sort_values("anio").reset_index(drop=True)


def cac_por_canal(marketing_spend: pd.DataFrame, customers: pd.DataFrame, anio: int) -> pd.DataFrame:
    """channel, gasto, clientes_nuevos y cac (1 dec.), ordenado por cac ascendente."""
    g = marketing_spend[marketing_spend["date"].dt.year == anio].groupby("channel")["spend_eur"].sum().rename("gasto")
    c = customers[customers["signup_date"].dt.year == anio].groupby("acquisition_channel").size().rename("clientes_nuevos")
    t = pd.concat([g, c.rename_axis("channel")], axis=1).dropna().rename_axis("channel").reset_index()
    t["clientes_nuevos"] = t["clientes_nuevos"].astype(int)
    t["cac"] = (t["gasto"] / t["clientes_nuevos"]).round(1)
    t["gasto"] = t["gasto"].round(0)
    return t.sort_values("cac").reset_index(drop=True)


def payback_meses(margen_mensual: pd.Series, cac: float):
    """Primer mes en que el margen acumulado >= cac, o None."""
    acumulado = margen_mensual.sort_index().cumsum()
    alcanzado = acumulado[acumulado >= cac]
    return int(alcanzado.index[0]) if len(alcanzado) else None


print(cac_por_anio(marketing_spend, customers))
print(cac_por_canal(marketing_spend, customers, 2025))
print(payback_meses(margen_mensual, 78.09), payback_meses(margen_mensual, 400))
