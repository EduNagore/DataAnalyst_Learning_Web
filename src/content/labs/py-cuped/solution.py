import numpy as np
import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
asignaciones = load_table("experiment_assignments")
experimentos = load_table("experiments")

exp = experimentos[experimentos["experiment_id"] == "exp-onboarding-flow"].iloc[0]
asignados = asignaciones[asignaciones["experiment_id"] == "exp-onboarding-flow"].reset_index(drop=True)
inicio, fin = exp["start_date"], exp["end_date"]
tratamiento = (asignados["variant"] == "tratamiento").to_numpy()


def ingresos_por_cliente(orders, order_items, clientes, inicio, fin) -> np.ndarray:
    """Ingresos (sin cancelados) de cada cliente de `clientes` entre `inicio` y `fin` (ambos incluidos)."""
    por_pedido = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    ped = orders[(orders["status"] != "cancelado") & orders["order_date"].between(inicio, fin)].copy()
    ped["importe"] = ped["order_id"].map(por_pedido).fillna(0.0)
    por_cliente = ped.groupby("customer_id")["importe"].sum()
    return pd.Series(clientes).map(por_cliente).fillna(0.0).to_numpy()


def theta_cuped(x, y) -> float:
    """θ = Cov(X, Y) / Var(X)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return float(np.cov(x, y)[0, 1] / x.var(ddof=1))


def ajustar_cuped(y, x) -> np.ndarray:
    """Métrica ajustada: y - θ (x - media(x))."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return y - theta_cuped(x, y) * (x - x.mean())


def efecto_y_error(y, tratamiento) -> tuple[float, float]:
    """(media tratamiento - media control, error estándar de Welch)."""
    y, t = np.asarray(y, dtype=float), np.asarray(tratamiento, dtype=bool)
    yt, yc = y[t], y[~t]
    se = np.sqrt(yt.var(ddof=1) / len(yt) + yc.var(ddof=1) / len(yc))
    return float(yt.mean() - yc.mean()), float(se)


def reduccion_varianza(x, y) -> float:
    """Fracción de la varianza de y que elimina el ajuste CUPED."""
    y = np.asarray(y, dtype=float)
    return float(1 - ajustar_cuped(y, x).var(ddof=1) / y.var(ddof=1))


clientes = asignados["customer_id"].to_numpy()
x = ingresos_por_cliente(orders, order_items, clientes, inicio - pd.Timedelta(days=90), inicio - pd.Timedelta(days=1))
y = ingresos_por_cliente(orders, order_items, clientes, inicio, fin)
print("correlación:", round(float(np.corrcoef(x, y)[0, 1]), 3))
print("sin ajustar:", efecto_y_error(y, tratamiento))
print("con CUPED:", efecto_y_error(ajustar_cuped(y, x), tratamiento))
print("varianza eliminada:", round(reduccion_varianza(x, y), 4))

rng = np.random.default_rng(0)
xs = rng.normal(size=20000)
ys = 0.75 * xs + np.sqrt(1 - 0.75**2) * rng.normal(size=20000)
print("simulación ρ = 0,75 → varianza eliminada:", round(reduccion_varianza(xs, ys), 3))
