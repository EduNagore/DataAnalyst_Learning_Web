import pandas as pd
from datakit.testing import assert_columns, assert_frame_equivalent


def test_valor_por_cliente(ns):
    """El gasto por cliente activo (792 y 853 €) supera al gasto por cliente captado (580 y 636 €)"""
    r = ns["valor_por_cliente"](ns["cohortes"])
    assert_columns(r, ["anio", "clientes", "activos", "gasto_por_activo", "gasto_por_captado"])
    esperado = pd.DataFrame(
        {
            "anio": [2023, 2024],
            "clientes": [11039, 15820],
            "activos": [8083, 11798],
            "gasto_por_activo": [792.0, 853.0],
            "gasto_por_captado": [580.0, 636.0],
        }
    )
    assert_frame_equivalent(r, esperado, sort_by=["anio"], tol=1.01)


def test_regresion_a_la_media(ns):
    """El 10 % superior del 1.er semestre gasta un 82 % menos en el 2.º (ratio 0,18)"""
    r = ns["regresion_a_la_media"](ns["h1"], ns["h2"])
    assert set(r) == {"n", "h1_medio", "h2_medio", "ratio", "correlacion"}, f"Claves: {sorted(r)}"
    assert abs(r["n"] - 2281) <= 2, f"n = {r['n']}"
    assert abs(r["h1_medio"] - 3577) <= 2 and abs(r["h2_medio"] - 633) <= 2, f"Medias: {r}"
    assert abs(r["ratio"] - 0.18) < 0.011 and abs(r["correlacion"] - 0.154) < 0.0025, f"Resultado: {r}"


def test_precision_de_la_alerta(ns):
    """Con tasa base 6,26 %, sensibilidad 80 % y especificidad 90 %, la precisión es 34,8 %"""
    r = ns["precision_alerta"](0.80, 0.90, 0.0626)
    assert abs(r["precision_pct"] - 34.8) < 0.11, f"Precisión: {r}"
    assert abs(r["falsos_por_verdadero"] - 1.87) < 0.011, f"Falsos por verdadero: {r}"


def test_hidden_casos_extremos(ns):
    """Una prueba muy buena con tasa base baja sigue dando muchas falsas alarmas; con tasa base alta, pocas (test oculto)"""
    baja = ns["precision_alerta"](0.99, 0.99, 0.001)
    alta = ns["precision_alerta"](0.99, 0.99, 0.5)
    assert abs(baja["precision_pct"] - 9.0) < 0.11, f"Tasa base baja: {baja}"
    assert abs(alta["precision_pct"] - 99.0) < 0.11, f"Tasa base alta: {alta}"
    h1 = pd.Series([10.0, 20.0, 30.0, 40.0, 100.0])
    h2 = pd.Series([25.0, 25.0, 30.0, 35.0, 50.0])
    r = ns["regresion_a_la_media"](h1, h2, q=0.8)
    assert r["n"] == 1 and r["h1_medio"] == 100.0 and r["h2_medio"] == 50.0 and r["ratio"] == 0.5, f"Resultado: {r}"
