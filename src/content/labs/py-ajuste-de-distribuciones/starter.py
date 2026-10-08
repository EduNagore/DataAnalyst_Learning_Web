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
    # TODO
    ...


def cola(x: pd.Series, umbral: float, mu: float, sigma: float) -> dict:
    """real_pct y modelo_pct (2 decimales): % de x por encima del umbral y P(X > umbral) en la log-normal."""
    # TODO
    ...


def dispersion(conteos: pd.Series) -> float:
    """varianza / media (2 decimales)."""
    # TODO
    ...


def ruido_binomial(p: float, n: int) -> float:
    """sqrt(p(1-p)/n) en puntos porcentuales (3 decimales)."""
    # TODO
    ...


par = ajuste_lognormal(importes)
print(par)
print(cola(importes, 1000, par["mu"], par["sigma"]), cola(importes, 2000, par["mu"], par["sigma"]))
print(dispersion(pedidos_dia), ruido_binomial(0.0424, 707))
