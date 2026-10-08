import numpy as np
from datakit.data import load_table


def test_posterior_y_resumen(ns):
    """prod-00019 (57 de 510) con prior plano: media 11,3 %, IC creíble [8,7 %; 14,2 %], P(>10 %) = 0,83"""
    a, b = ns["posterior_beta"](57, 510)
    assert (a, b) == (58.0, 454.0), f"Posterior: ({a}, {b})"
    r = ns["resumen_posterior"](a, b)
    assert abs(r["media"] - 0.1133) < 0.0005
    assert abs(r["inferior"] - 0.0873) < 0.001 and abs(r["superior"] - 0.1421) < 0.001
    assert abs(r["p_mayor_que"](0.10) - 0.828) < 0.005


def test_prior_informado(ns):
    """Con un prior del 7,0 % y peso 400, la media baja a 9,3 % y P(>10 %) a 0,24"""
    a, b = ns["posterior_beta"](57, 510, 28.07, 371.93)
    r = ns["resumen_posterior"](a, b)
    assert abs(r["media"] - 0.0935) < 0.0005 and abs(r["p_mayor_que"](0.10) - 0.244) < 0.005


def test_comparacion_por_canal(ns):
    """Cancelación: online 14.657/365.198 frente a tienda 1.104/27.708 → P(tienda > online) ≈ 0,41"""
    a1, b1 = ns["posterior_beta"](14657, 365198)
    a2, b2 = ns["posterior_beta"](1104, 27708)
    p = ns["prob_mayor"](a1, b1, a2, b2, n_sim=200000, seed=0)
    assert abs(p - 0.41) < 0.01, f"P = {p:.3f}"
    assert ns["prob_mayor"](a1, b1, a2, b2, n_sim=1000, seed=3) == ns["prob_mayor"](a1, b1, a2, b2, n_sim=1000, seed=3)


def test_ranking_encogido(ns):
    """2.000 productos; el primero por tasa encogida sigue siendo prod-00019 pero con 9,3 % en lugar de 11,2 %"""
    r = ns["ranking_encogido"](load_table("order_items"), load_table("returns"))
    assert list(r.columns) == ["product_id", "k", "n", "tasa", "tasa_bayes"], f"Columnas: {list(r.columns)}"
    assert len(r) == 2000 and r["tasa_bayes"].is_monotonic_decreasing
    top = r.iloc[0]
    assert top["product_id"] == "prod-00019" and top["k"] == 57 and top["n"] == 510
    assert abs(top["tasa"] - 0.1118) < 0.0005 and abs(top["tasa_bayes"] - 0.0935) < 0.0005


def test_hidden_propiedades_del_encogimiento(ns):
    """El encogimiento acerca a la media global y su fuerza controla cuánto (test oculto)"""
    oi, ret = load_table("order_items"), load_table("returns")
    suave = ns["ranking_encogido"](oi, ret, fuerza=50).set_index("product_id")
    fuerte = ns["ranking_encogido"](oi, ret, fuerza=2000).set_index("product_id")
    media = suave["k"].sum() / suave["n"].sum()
    for df in (suave, fuerte):
        assert ((df["tasa_bayes"] - media).abs() <= (df["tasa"] - media).abs() + 1e-12).all()
    assert fuerte["tasa_bayes"].std() < suave["tasa_bayes"].std()
    # sin datos, el posterior es el prior; con muchos datos, domina la tasa observada
    a, b = ns["posterior_beta"](0, 0, 2.0, 8.0)
    assert (a, b) == (2.0, 8.0)
    a, b = ns["posterior_beta"](300000, 1000000, 2.0, 8.0)
    assert abs(ns["resumen_posterior"](a, b)["media"] - 0.3) < 1e-4
    r90 = ns["resumen_posterior"](5.0, 20.0, nivel=0.90)
    r99 = ns["resumen_posterior"](5.0, 20.0, nivel=0.99)
    assert r99["inferior"] < r90["inferior"] < r90["superior"] < r99["superior"]
    assert np.isclose(ns["resumen_posterior"](5, 20)["p_mayor_que"](0.0), 1.0)
