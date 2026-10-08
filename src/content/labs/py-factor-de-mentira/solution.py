import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
customers = load_table("customers")

pedidos = orders[orders["status"] != "cancelado"].groupby(orders["order_date"].dt.to_period("M")).size()
altas = customers.groupby(customers["signup_date"].dt.to_period("M")).size()
mensual = pd.concat([pedidos.rename("pedidos"), altas.rename("altas")], axis=1).dropna().iloc[1:-1]
print(mensual.shape, mensual.index[0], mensual.index[-1])


def factor_de_mentira(v1: float, v2: float, eje_min: float) -> float:
    """Cambio relativo dibujado / cambio relativo del dato (1 decimal)."""
    h1, h2 = v1 - eje_min, v2 - eje_min
    visual = (h2 - h1) / h1
    dato = (v2 - v1) / v1
    return round(visual / dato, 1)


def correlaciones_niveles_y_cambios(df: pd.DataFrame, a: str, b: str) -> tuple[float, float]:
    """(correlación de niveles, correlación de diferencias mensuales), 3 decimales."""
    niveles = float(df[a].corr(df[b]))
    d = df[[a, b]].diff().dropna()
    cambios = float(d[a].corr(d[b]))
    return round(niveles, 3), round(cambios, 3)


print(factor_de_mentira(301.4, 302.0, 301.0), factor_de_mentira(301.4, 302.0, 0))
print(correlaciones_niveles_y_cambios(mensual, "pedidos", "altas"))
