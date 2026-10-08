import numpy as np
from datakit.data import load_table
from scipy import stats


def _serie(exp_id, metrica):
    m = load_table("experiment_metrics")
    x = m[(m["experiment_id"] == exp_id) & (m["metric_name"] == metrica)]
    return (
        x.loc[x["variant"] == "tratamiento", "value"].to_numpy(),
        x.loc[x["variant"] == "control", "value"].to_numpy(),
    )


def test_welch_checkout(ns):
    """exp-checkout-v2: t = 5,34, gl = 55,6 y p = 1,8e-6"""
    tr, co = _serie("exp-checkout-v2", "conversion_rate")
    t, gl, p = ns["welch_t"](tr, co)
    assert abs(t - 5.3423) < 0.001, f"t = {t:.4f}"
    assert abs(gl - 55.589) < 0.01, f"gl = {gl:.3f}"
    assert 1.6e-6 < p < 1.9e-6, f"p = {p:.3e}"


def test_welch_nulo_y_signo(ns):
    """Un experimento sin efecto (p ≈ 0,36) y el signo del estadístico al invertir los grupos"""
    tr, co = _serie("exp-generic-08", "revenue_per_user")
    t, _, p = ns["welch_t"](tr, co)
    assert abs(p - 0.3635) < 0.002 and t < 0
    t2, _, p2 = ns["welch_t"](co, tr)
    assert abs(t2 + t) < 1e-9 and abs(p2 - p) < 1e-12


def test_tamano_y_potencia(ns):
    """+8 % sobre 5,4 % necesita 44.582 por grupo; con 10.000 la potencia es 0,264"""
    assert ns["tamano_muestra"](0.054, 0.08) == 44582
    assert ns["tamano_muestra"](0.05, 0.10) == 31231
    assert abs(ns["potencia"](0.054, 0.08, 10000) - 0.264) < 0.002
    assert abs(ns["potencia"](0.054, 0.08, 44582) - 0.80) < 0.005


def test_hidden_simulacion_y_monotonia(ns):
    """La simulación concuerda con la fórmula y la potencia crece con n, MDE y alpha (test oculto)"""
    analitica = ns["potencia"](0.054, 0.10, 20000)
    simulada = ns["potencia_simulada"](0.054, 0.10, 20000, n_sim=3000, seed=2)
    assert abs(analitica - simulada) < 0.04, f"analítica {analitica:.3f} vs simulada {simulada:.3f}"
    assert ns["potencia_simulada"](0.054, 0.10, 20000, n_sim=500, seed=5) == ns["potencia_simulada"](
        0.054, 0.10, 20000, n_sim=500, seed=5
    )
    assert ns["potencia"](0.05, 0.1, 20000) > ns["potencia"](0.05, 0.1, 10000)
    assert ns["potencia"](0.05, 0.2, 10000) > ns["potencia"](0.05, 0.1, 10000)
    assert ns["potencia"](0.05, 0.1, 10000, alpha=0.10) > ns["potencia"](0.05, 0.1, 10000, alpha=0.05)
    assert ns["tamano_muestra"](0.05, 0.1, potencia=0.9) > ns["tamano_muestra"](0.05, 0.1, potencia=0.8)
    # sin efecto, la tasa de rechazo debe ser ≈ alpha
    nula = ns["potencia_simulada"](0.05, 0.0, 5000, n_sim=4000, seed=1)
    assert abs(nula - 0.05) < 0.02, f"Tasa de falsos positivos: {nula:.3f}"
    assert isinstance(ns["tamano_muestra"](0.05, 0.1), (int, np.integer))
    assert stats.norm.cdf(0) == 0.5
