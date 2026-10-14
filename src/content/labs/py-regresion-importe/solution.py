import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

orders = load_table("orders")
order_items = load_table("order_items")


def datos_pedidos(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    """Pedidos completados con importe > 0: ln_importe, lineas, unidades, ln_lineas y discount_pct."""
    g = (
        order_items.assign(importe=order_items["quantity"] * order_items["unit_price"])
        .groupby("order_id")
        .agg(importe=("importe", "sum"), lineas=("order_id", "size"), unidades=("quantity", "sum"))
    )
    d = orders.loc[orders["status"] == "completado", ["order_id", "discount_pct"]].join(g, on="order_id")
    d = d[d["importe"] > 0].copy()
    d["ln_importe"] = np.log(d["importe"])
    d["ln_lineas"] = np.log(d["lineas"])
    return d.reset_index(drop=True)


def ols(df: pd.DataFrame, y: str, x: list[str]) -> dict:
    """OLS con constante: devuelve `tabla` (coef, se, t, p, ic_inf, ic_sup por término) y `r2`."""
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(dtype=float) for c in x])
    yv = df[y].to_numpy(dtype=float)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ yv
    resid = yv - X @ beta
    gl = len(yv) - X.shape[1]
    sigma2 = resid @ resid / gl
    se = np.sqrt(sigma2 * np.diag(XtX_inv))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), gl)
    tcrit = stats.t.ppf(0.975, gl)
    tabla = pd.DataFrame(
        {"coef": beta, "se": se, "t": t, "p": p, "ic_inf": beta - tcrit * se, "ic_sup": beta + tcrit * se},
        index=["const"] + list(x),
    )
    r2 = 1 - (resid @ resid) / np.sum((yv - yv.mean()) ** 2)
    return {"tabla": tabla, "r2": float(r2)}


def efecto_pct(beta: float, delta: float = 1.0) -> float:
    """Cambio porcentual de y cuando x sube `delta` en un modelo con ln(y): 100 (exp(beta·delta) - 1)."""
    return float(100 * (np.exp(beta * delta) - 1))


def vif(df: pd.DataFrame, x: list[str]) -> dict:
    """Factor de inflación de la varianza de cada variable de `x`."""
    out = {}
    for c in x:
        otras = [o for o in x if o != c]
        r2 = ols(df, c, otras)["r2"] if otras else 0.0
        out[c] = float(1 / (1 - r2))
    return out


d = datos_pedidos(orders, order_items)
a = ols(d, "ln_importe", ["lineas", "discount_pct"])
b = ols(d, "ln_importe", ["ln_lineas", "discount_pct"])
print("A: R2 =", round(a["r2"], 3))
print(a["tabla"].round(4))
print("B: R2 =", round(b["r2"], 3))
print("-10 puntos de descuento →", round(efecto_pct(b["tabla"].loc["discount_pct", "coef"], 0.1), 1), "% de importe")
print("VIF:", {k: round(v, 2) for k, v in vif(d, ["lineas", "unidades", "discount_pct"]).items()})
