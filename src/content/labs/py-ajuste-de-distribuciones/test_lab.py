import numpy as np
import pandas as pd


def test_ajuste(ns):
    """mu = 5,055 y sigma = 1,277 para los importes de pedido"""
    r = ns["ajuste_lognormal"](ns["importes"])
    assert abs(r["mu"] - 5.055) < 0.0015 and abs(r["sigma"] - 1.277) < 0.0015, f"Ajuste: {r}"


def test_colas(ns):
    """La log-normal sobrestima la cola: 7,35 % frente al 4,90 % real por encima de 1.000 €"""
    par = ns["ajuste_lognormal"](ns["importes"])
    c1 = ns["cola"](ns["importes"], 1000, par["mu"], par["sigma"])
    c2 = ns["cola"](ns["importes"], 2000, par["mu"], par["sigma"])
    assert abs(c1["real_pct"] - 4.90) < 0.011 and abs(c1["modelo_pct"] - 7.35) < 0.06, f"Cola 1000: {c1}"
    assert abs(c2["real_pct"] - 0.62) < 0.011 and abs(c2["modelo_pct"] - 2.31) < 0.06, f"Cola 2000: {c2}"


def test_dispersion_y_ruido(ns):
    """Varianza/media de los pedidos diarios = 1,24 y ruido binomial = 0,758 puntos"""
    assert abs(ns["dispersion"](ns["pedidos_dia"]) - 1.24) < 0.011
    assert abs(ns["ruido_binomial"](0.0424, 707) - 0.758) < 0.002


def test_hidden_muestras_sinteticas(ns):
    """Recupera los parámetros de una log-normal sintética y detecta una Poisson (test oculto)"""
    rng = np.random.default_rng(7)
    x = pd.Series(rng.lognormal(mean=4.0, sigma=0.5, size=200_000))
    r = ns["ajuste_lognormal"](x)
    assert abs(r["mu"] - 4.0) < 0.01 and abs(r["sigma"] - 0.5) < 0.01, f"Ajuste: {r}"
    c = ns["cola"](x, float(np.exp(4.0)), r["mu"], r["sigma"])
    assert abs(c["modelo_pct"] - 50.0) < 0.5 and abs(c["real_pct"] - 50.0) < 0.5, f"Mediana: {c}"
    pois = pd.Series(rng.poisson(30, size=100_000))
    assert abs(ns["dispersion"](pois) - 1.0) < 0.03, "En una Poisson la varianza es igual a la media."
