import numpy as np
import pandas as pd
from datakit.data import load_table


def _datos():
    asig = load_table("experiment_assignments")
    asig = asig[asig["experiment_id"] == "exp-onboarding-flow"].reset_index(drop=True)
    exp = load_table("experiments")
    exp = exp[exp["experiment_id"] == "exp-onboarding-flow"].iloc[0]
    return asig, exp["start_date"], exp["end_date"]


def test_ingresos_y_correlacion(ns):
    """Ingresos previos (90 días) y del experimento: correlación 0,126 y media de 12,64 €"""
    asig, inicio, fin = _datos()
    clientes = asig["customer_id"].to_numpy()
    o, oi = load_table("orders"), load_table("order_items")
    x = ns["ingresos_por_cliente"](o, oi, clientes, inicio - pd.Timedelta(days=90), inicio - pd.Timedelta(days=1))
    y = ns["ingresos_por_cliente"](o, oi, clientes, inicio, fin)
    assert len(x) == len(y) == 20000
    assert abs(y.mean() - 12.64) < 0.02, f"Media de ingresos: {y.mean():.2f}"
    assert abs(np.corrcoef(x, y)[0, 1] - 0.126) < 0.005


def test_cuped_en_datos_reales(ns):
    """Error estándar 1,627 → 1,614 y varianza eliminada ≈ 1,6 % (el efecto verdadero es nulo)"""
    asig, inicio, fin = _datos()
    clientes = asig["customer_id"].to_numpy()
    t = (asig["variant"] == "tratamiento").to_numpy()
    o, oi = load_table("orders"), load_table("order_items")
    x = ns["ingresos_por_cliente"](o, oi, clientes, inicio - pd.Timedelta(days=90), inicio - pd.Timedelta(days=1))
    y = ns["ingresos_por_cliente"](o, oi, clientes, inicio, fin)
    d, se = ns["efecto_y_error"](y, t)
    assert abs(d - 0.247) < 0.01 and abs(se - 1.627) < 0.005, f"Sin ajustar: {d:.3f} ± {se:.3f}"
    d2, se2 = ns["efecto_y_error"](ns["ajustar_cuped"](y, x), t)
    assert abs(se2 - 1.614) < 0.005 and abs(d2 - 0.227) < 0.01, f"CUPED: {d2:.3f} ± {se2:.3f}"
    assert abs(ns["reduccion_varianza"](x, y) - 0.0158) < 0.002
    assert abs(ns["theta_cuped"](x, y) - 0.0764) < 0.003


def test_simulacion_con_correlacion_alta(ns):
    """Con ρ = 0,75 se elimina ≈ 56 % de la varianza y el efecto estimado no cambia"""
    rng = np.random.default_rng(0)
    n = 40000
    x = rng.normal(size=n)
    t = rng.random(n) < 0.5
    y = 0.75 * x + np.sqrt(1 - 0.75**2) * rng.normal(size=n) + 0.2 * t
    assert abs(ns["reduccion_varianza"](x, y) - 0.56) < 0.03
    d, se = ns["efecto_y_error"](y, t)
    d2, se2 = ns["efecto_y_error"](ns["ajustar_cuped"](y, x), t)
    assert abs(d - d2) < 0.03 and se2 < 0.75 * se


def test_hidden_propiedades(ns):
    """El ajuste conserva la media, θ de una relación exacta y los extremos de la ventana (test oculto)"""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = 3 * x + 1
    assert abs(ns["theta_cuped"](x, y) - 3) < 1e-9
    aj = ns["ajustar_cuped"](y, x)
    assert abs(aj.mean() - y.mean()) < 1e-9 and np.allclose(aj, aj[0])
    assert abs(ns["reduccion_varianza"](x, y) - 1) < 1e-9
    assert abs(ns["reduccion_varianza"](np.arange(10.0), np.ones(10) * 5 + np.tile([1.0, -1.0], 5))) < 0.2
    orders = pd.DataFrame(
        {
            "order_id": ["a", "b", "c", "d"],
            "customer_id": ["c1", "c1", "c1", "c2"],
            "order_date": pd.to_datetime(["2023-01-01", "2023-01-31", "2023-02-01", "2023-01-15"]),
            "status": ["completado", "cancelado", "completado", "completado"],
        }
    )
    items = pd.DataFrame(
        {
            "order_id": ["a", "b", "c", "d"],
            "quantity": [1, 1, 2, 1],
            "unit_price": [10.0, 100.0, 5.0, 7.0],
        }
    )
    r = ns["ingresos_por_cliente"](orders, items, np.array(["c1", "c2", "c3"]), pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-31"))
    assert list(r) == [10.0, 7.0, 0.0], "Incluye ambos extremos, excluye cancelados y rellena con 0."
