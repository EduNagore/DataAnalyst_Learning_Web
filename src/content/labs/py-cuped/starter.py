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
    # TODO
    ...


def theta_cuped(x, y) -> float:
    """θ = Cov(X, Y) / Var(X)."""
    # TODO
    ...


def ajustar_cuped(y, x) -> np.ndarray:
    """Métrica ajustada: y - θ (x - media(x))."""
    # TODO
    ...


def efecto_y_error(y, tratamiento) -> tuple[float, float]:
    """(media tratamiento - media control, error estándar de Welch)."""
    # TODO
    ...


def reduccion_varianza(x, y) -> float:
    """Fracción de la varianza de y que elimina el ajuste CUPED."""
    # TODO
    ...


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
