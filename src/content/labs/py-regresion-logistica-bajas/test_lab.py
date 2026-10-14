import numpy as np
import pandas as pd
from datakit.data import load_table
from datakit.lumen import panel_bajas


def _panel():
    p = panel_bajas(load_table("subscriptions"), load_table("shipments"), load_table("orders"))
    p["anual"] = (p["plan"] == "anual").astype(int)
    return p


def test_razones_de_odds(ns):
    """Retraso grave: OR ≈ 17,5 (16,7–18,5); plan, cuota y antigüedad no aportan (OR ≈ 1)"""
    t = ns["razones_de_odds"](_panel(), "cancela", ["expuesto", "anual", "mrr_eur", "k"])
    assert list(t.columns) == ["odds_ratio", "ic_inf", "ic_sup"] and list(t.index) == ["expuesto", "anual", "mrr_eur", "k"]
    e = t.loc["expuesto"]
    assert abs(e["odds_ratio"] - 17.54) < 0.15 and e["ic_inf"] < 17.54 < e["ic_sup"] and abs(e["ic_inf"] - 16.68) < 0.2
    assert t.loc["anual", "ic_inf"] < 1 < t.loc["anual", "ic_sup"]
    assert t.loc["mrr_eur", "ic_inf"] < 1 < t.loc["mrr_eur", "ic_sup"]


def test_coeficientes_y_errores(ns):
    """const −3,367 y expuesto 2,865 (error estándar 0,026)"""
    r = ns["ajustar_logit"](_panel(), "cancela", ["expuesto", "anual", "mrr_eur", "k"])
    assert abs(r["params"]["const"] + 3.3668) < 0.01 and abs(r["params"]["expuesto"] - 2.8647) < 0.01
    assert abs(r["se"]["expuesto"] - 0.0257) < 0.002 and list(r["params"].index)[0] == "const"


def test_auc_y_probabilidades(ns):
    """El AUC en muestra de todo el panel es ≈ 0,60: efecto enorme, poca capacidad de predicción"""
    p = _panel()
    r = ns["ajustar_logit"](p, "cancela", ["expuesto"])
    prob = ns["probabilidades"](p, r["params"])
    assert abs(prob[p["expuesto"].to_numpy() == 1][0] - 0.389) < 0.005 and abs(prob[p["expuesto"].to_numpy() == 0][0] - 0.035) < 0.002
    assert abs(ns["auc"](p["cancela"], prob) - 0.60) < 0.01


def test_hidden_auc_y_logit_sinteticos(ns):
    """AUC perfecto, aleatorio y con empates; recuperación de coeficientes conocidos (test oculto)"""
    assert ns["auc"]([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert ns["auc"]([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]) == 0.0
    assert abs(ns["auc"]([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5]) - 0.5) < 1e-12
    rng = np.random.default_rng(0)
    n = 50000
    x = rng.normal(size=n)
    y = (rng.random(n) < 1 / (1 + np.exp(-(-1 + 2 * x)))).astype(int)
    df = pd.DataFrame({"x": x, "y": y})
    r = ns["ajustar_logit"](df, "y", ["x"])
    assert abs(r["params"]["const"] + 1) < 0.05 and abs(r["params"]["x"] - 2) < 0.06
    assert abs(ns["razones_de_odds"](df, "y", ["x"]).loc["x", "odds_ratio"] - np.exp(2)) < 0.6
