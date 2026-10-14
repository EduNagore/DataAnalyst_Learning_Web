import numpy as np
import pandas as pd
from datakit.data import load_table


def _res(ns):
    return ns["resumen_clientes"](load_table("orders"), load_table("order_items"), ns["CORTE"])


def test_parametros_bgnbd(ns):
    """BG/NBD: r ≈ 0,48, α ≈ 2,04, a ≈ 1,79, b ≈ 10,2 con 23.278 clientes"""
    res = _res(ns)
    assert len(res) == 23278
    p = ns["ajustar_bgnbd"](res)
    assert abs(p["r"] - 0.484) < 0.015 and abs(p["alpha"] - 2.04) < 0.08
    assert abs(p["a"] - 1.79) < 0.08 and abs(p["b"] - 10.2) < 0.5


def test_calibracion_agregada(ns):
    """Compras de 2025: ≈ 47.100 previstas frente a 49.495 reales (−4,8 %)"""
    res = _res(ns)
    p = ns["ajustar_bgnbd"](res)
    pred = ns["compras_esperadas"](res, p, 52).sum()
    assert abs(pred - 47120) < 600
    o = load_table("orders")
    o = o[o["status"] != "cancelado"].copy()
    o["dia"] = pd.to_datetime(o["order_date"]).dt.normalize()
    ventana = o[(o["dia"] > ns["CORTE"]) & (o["dia"] <= ns["CORTE"] + pd.Timedelta(days=364))]
    real = ventana.groupby("customer_id")["dia"].nunique()
    real = real.reindex(res.index, fill_value=0)
    assert real.sum() == 49495 and abs(pred / real.sum() - 1) < 0.08


def test_clv_en_euros(ns):
    """Gamma-Gamma + BG/NBD: ingresos previstos de 2025 ≈ 14,85 M€ (reales: 15,16 M€)"""
    res = _res(ns)
    bg, gg = ns["ajustar_bgnbd"](res), ns["ajustar_gamma_gamma"](res)
    assert abs(gg["p"] - 0.918) < 0.03
    total = ns["clv"](res, bg, gg, 52).sum()
    assert abs(total / 1e6 - 14.85) < 0.25
    assert abs(ns["valor_esperado"](res, gg).mean() - 314) < 6


def test_hidden_cliente_nuevo_frente_a_simulacion(ns):
    """Compras esperadas de un cliente nuevo = media de una simulación del proceso BG/NBD (test oculto)"""
    params = {"r": 0.48, "alpha": 2.0, "a": 1.8, "b": 10.0}
    nuevo = pd.DataFrame({"x": [0.0], "tx": [0.0], "T": [0.0]})
    esperado = float(ns["compras_esperadas"](nuevo, params, 52)[0])
    rng = np.random.default_rng(1)
    n = 100000
    lam, p = rng.gamma(params["r"], 1 / params["alpha"], n), rng.beta(params["a"], params["b"], n)
    vida, acum, tot, activo, k = rng.geometric(p), np.zeros(n), np.zeros(n), np.ones(n, bool), 0
    while activo.any() and k < 3000:
        k += 1
        acum += rng.exponential(1 / lam)
        activo &= (acum <= 52) & (k <= vida)
        tot += activo
    assert abs(esperado / tot.mean() - 1) < 0.03, f"esperado {esperado:.2f} frente a simulado {tot.mean():.2f}"
    ll = ns["loglik_bgnbd"](params, pd.DataFrame({"x": [0.0, 3.0], "tx": [0.0, 20.0], "T": [30.0, 30.0]}))
    assert np.all(np.isfinite(ll)) and np.all(ll < 0)
