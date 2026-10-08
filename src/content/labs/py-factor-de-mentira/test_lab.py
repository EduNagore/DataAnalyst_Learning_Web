import pandas as pd


def test_factor_de_mentira(ns):
    """El eje recortado en 301 € multiplica por ≈ 754 la diferencia entre 301,4 € y 302,0 €"""
    f = ns["factor_de_mentira"]
    assert abs(f(301.4, 302.0, 301.0) - 753.5) < 0.6, f"Factor: {f(301.4, 302.0, 301.0)}"
    assert f(301.4, 302.0, 0) == 1.0, "Con el eje en cero el factor debe ser 1."


def test_otro_recorte(ns):
    """De 90 a 99 con el eje recortado en 80, el cambio dibujado (+90 %) es 9 veces el del dato (+10 %)"""
    assert ns["factor_de_mentira"](90, 99, 80) == 9.0, ns["factor_de_mentira"](90, 99, 80)


def test_correlaciones(ns):
    """Niveles 0,977 y cambios 0,301 entre pedidos y altas"""
    n, c = ns["correlaciones_niveles_y_cambios"](ns["mensual"], "pedidos", "altas")
    assert abs(n - 0.977) < 0.002 and abs(c - 0.301) < 0.003, f"Correlaciones: {(n, c)}"
    assert c < n - 0.5, "La correlación de los cambios debería ser mucho menor que la de los niveles."


def test_hidden_series_con_tendencia(ns):
    """Dos series independientes con tendencia: alta en niveles y casi nula en cambios (test oculto)"""
    import numpy as np

    rng = np.random.default_rng(5)
    t = np.arange(120)
    df = pd.DataFrame({"a": t * 2.0 + rng.normal(0, 3, 120), "b": t * 5.0 + rng.normal(0, 8, 120)})
    n, c = ns["correlaciones_niveles_y_cambios"](df, "a", "b")
    assert n > 0.95, f"Niveles: {n}"
    assert abs(c) < 0.25, f"Cambios: {c}"
