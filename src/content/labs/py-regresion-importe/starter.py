import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

orders = load_table("orders")
order_items = load_table("order_items")


def datos_pedidos(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    """Pedidos completados con importe > 0: ln_importe, lineas, unidades, ln_lineas y discount_pct."""
    # TODO
    ...


def ols(df: pd.DataFrame, y: str, x: list[str]) -> dict:
    """OLS con constante: devuelve `tabla` (coef, se, t, p, ic_inf, ic_sup por término) y `r2`."""
    # TODO
    ...


def efecto_pct(beta: float, delta: float = 1.0) -> float:
    """Cambio porcentual de y cuando x sube `delta` en un modelo con ln(y): 100 (exp(beta·delta) - 1)."""
    # TODO
    ...


def vif(df: pd.DataFrame, x: list[str]) -> dict:
    """Factor de inflación de la varianza de cada variable de `x`."""
    # TODO
    ...


d = datos_pedidos(orders, order_items)
a = ols(d, "ln_importe", ["lineas", "discount_pct"])
b = ols(d, "ln_importe", ["ln_lineas", "discount_pct"])
print("A: R2 =", round(a["r2"], 3))
print(a["tabla"].round(4))
print("B: R2 =", round(b["r2"], 3))
print("-10 puntos de descuento →", round(efecto_pct(b["tabla"].loc["discount_pct", "coef"], 0.1), 1), "% de importe")
print("VIF:", {k: round(v, 2) for k, v in vif(d, ["lineas", "unidades", "discount_pct"]).items()})
