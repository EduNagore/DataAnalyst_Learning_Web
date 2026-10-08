import numpy as np
import pandas as pd


def test_condicionales(ns):
    """P(cancela | retraso grave) = 63,0 % y P(retraso grave | cancela) = 59,5 %: no son lo mismo"""
    subs = ns["subs"]
    directa = ns["p_condicional"](subs, "cancela", "retraso_grave")
    inversa = ns["p_condicional"](subs, "retraso_grave", "cancela")
    assert abs(directa - 63.0) < 0.06, f"P(cancela | retraso grave) = {directa}"
    assert abs(inversa - 59.5) < 0.06, f"P(retraso grave | cancela) = {inversa}"


def test_bayes(ns):
    """Bayes reproduce 0,630 a partir de 0,595, 0,565 y 0,534"""
    assert abs(ns["bayes"](0.595, 0.565, 0.534) - 0.630) < 0.0015
    subs = ns["subs"]
    p_b_a = subs.loc[subs["cancela"], "retraso_grave"].mean()
    r = ns["bayes"](float(p_b_a), float(subs["cancela"].mean()), float(subs["retraso_grave"].mean()))
    assert abs(r - subs.loc[subs["retraso_grave"], "cancela"].mean()) < 0.002, "Bayes debe coincidir con la condicional directa."


def test_independencia(ns):
    """Devolución y electrónica son independientes; retraso grave y cancelación no"""
    assert ns["independientes"](ns["lineas"], "devuelta", "es_electronica") is True
    assert ns["independientes"](ns["subs"], "cancela", "retraso_grave") is False


def test_hidden_tablas_pequenas(ns):
    """Una tabla claramente dependiente y otra independiente (test oculto)"""
    rng = np.random.default_rng(3)
    a = rng.random(5000) < 0.3
    dep = pd.DataFrame({"x": a, "y": np.where(a, rng.random(5000) < 0.8, rng.random(5000) < 0.1)})
    ind = pd.DataFrame({"x": rng.random(5000) < 0.3, "y": rng.random(5000) < 0.4})
    assert ns["independientes"](dep, "x", "y") is False
    assert ns["independientes"](ind, "x", "y") is True
    assert abs(ns["p_condicional"](dep, "y", "x") - 80.0) < 3.0, "P(y|x) debería rondar el 80 %."
