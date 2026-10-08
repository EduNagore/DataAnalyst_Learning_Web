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
    # TODO
    ...


def correlaciones_niveles_y_cambios(df: pd.DataFrame, a: str, b: str) -> tuple[float, float]:
    """(correlación de niveles, correlación de diferencias mensuales), 3 decimales."""
    # TODO
    ...


print(factor_de_mentira(301.4, 302.0, 301.0), factor_de_mentira(301.4, 302.0, 0))
print(correlaciones_niveles_y_cambios(mensual, "pedidos", "altas"))
