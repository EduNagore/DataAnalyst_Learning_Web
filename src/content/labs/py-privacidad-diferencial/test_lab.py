import numpy as np
import pandas as pd


def test_el_error_es_uno_entre_epsilon(ns):
    """El error absoluto medio del mecanismo de Laplace es sensibilidad / epsilon: ≈ 1 con ε = 1 y ≈ 10 con ε = 0,1"""
    c = ns["por_region"]
    assert abs(ns["error_absoluto_medio"](c, 1.0) - 1.0) < 0.05
    assert abs(ns["error_absoluto_medio"](c, 0.1) - 10.0) < 0.5
    assert abs(ns["error_absoluto_medio"](c, 5.0) - 0.2) < 0.01


def test_privacidad_frente_a_utilidad(ns):
    """Con ε = 1, el error relativo por región es 0,05 %; en las 384 celdas región×segmento×canal, 1,8 % (celdas pequeñas)"""
    assert abs(ns["error_relativo_medio"](ns["por_region"], 1.0) - 0.048) < 0.005
    assert abs(ns["error_relativo_medio"](ns["por_celda"], 1.0) - 1.79) < 0.08
    assert abs(ns["error_relativo_medio"](ns["por_celda"], 0.1) - 17.9) < 0.8


def test_conteos_privados(ns):
    """El histograma ruidoso conserva el índice, no tiene negativos y es reproducible con la misma semilla"""
    c = ns["por_region"]
    a, b = ns["conteos_privados"](c, 1.0, semilla=7), ns["conteos_privados"](c, 1.0, semilla=7)
    assert list(a.index) == list(c.index) and (a >= 0).all() and a.equals(b)
    assert not a.equals(ns["conteos_privados"](c, 1.0, semilla=8))
    assert np.abs(a - c).max() < 15 and a.sum() > 0


def test_hidden_presupuesto_y_epsilon(ns):
    """Composición secuencial, epsilon para un error objetivo y recorte de negativos (test oculto)"""
    assert abs(ns["presupuesto_total"]([0.1, 0.2, 0.7]) - 1.0) < 1e-12
    assert abs(ns["epsilon_para_error"](5.0) - 0.2) < 1e-12
    assert abs(ns["epsilon_para_error"](10.0, sensibilidad=2.0) - 0.2) < 1e-12
    pequeno = pd.Series([0, 1, 2], index=["a", "b", "c"])
    r = ns["conteos_privados"](pequeno, 0.05, semilla=3)
    assert (r >= 0).all(), "El recorte a cero es post-procesado y no gasta privacidad."
    rng = np.random.default_rng(0)
    ruido = ns["ruido_laplace"](2.0, rng, 50000)
    assert abs(np.abs(ruido).mean() - 0.5) < 0.02 and abs(ruido.mean()) < 0.02
