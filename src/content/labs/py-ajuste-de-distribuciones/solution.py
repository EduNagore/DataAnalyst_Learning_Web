import math

import numpy as np
import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")

por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
ok = orders[orders["status"] != "cancelado"]
importes = por_pedido.reindex(ok["order_id"]).reset_index(drop=True)
dias = ok.groupby("order_date").size()
pedidos_dia = dias[(dias.index >= "2025-04-01") & (dias.index <= "2025-05-31")]
print(len(importes), len(pedidos_dia))


def ajuste_lognormal(x: pd.Series) -> dict:
    """mu y sigma (3 decimales) de ln(x)."""
    lx = np.log(x)
    return {"mu": round(float(lx.mean()), 3), "sigma": round(float(lx.std()), 3)}


def cola(x: pd.Series, umbral: float, mu: float, sigma: float) -> dict:
    """real_pct y modelo_pct (2 decimales): % de x por encima del umbral y P(X > umbral) en la log-normal."""
    z = (math.log(umbral) - mu) / sigma
    phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return {"real_pct": round(float((x > umbral).mean() * 100), 2), "modelo_pct": round((1 - phi) * 100, 2)}


def dispersion(conteos: pd.Series) -> float:
    """varianza / media (2 decimales)."""
    return round(float(conteos.var() / conteos.mean()), 2)


def ruido_binomial(p: float, n: int) -> float:
    """sqrt(p(1-p)/n) en puntos porcentuales (3 decimales)."""
    return round(math.sqrt(p * (1 - p) / n) * 100, 3)


par = ajuste_lognormal(importes)
print(par)
print(cola(importes, 1000, par["mu"], par["sigma"]), cola(importes, 2000, par["mu"], par["sigma"]))
print(dispersion(pedidos_dia), ruido_binomial(0.0424, 707))
