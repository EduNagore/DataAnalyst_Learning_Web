import pandas as pd


def test_resumen(ns):
    """Media 0,58, mediana 0, desviación 2,64, IQR 1, P90 5, P95 8 y P99 10"""
    r = ns["resumen_retrasos"](ns["retraso"])
    assert set(r) == {"n", "media", "mediana", "desviacion", "iqr", "p90", "p95", "p99"}, f"Claves: {sorted(r)}"
    assert r["n"] == 365198, f"n = {r['n']}"
    assert abs(r["media"] - 0.58) < 0.006 and abs(r["desviacion"] - 2.64) < 0.006, f"Resumen: {r}"
    assert r["mediana"] == 0 and r["iqr"] == 1 and r["p90"] == 5 and r["p95"] == 8 and r["p99"] == 10, f"Resumen: {r}"


def test_cumple_sla(ns):
    """El 82,0 % de los envíos llega a tiempo (retraso <= 0) y el 89,3 % con 4 días o menos"""
    assert abs(ns["cumple_sla"](ns["retraso"], 0) - 82.0) < 0.11
    assert abs(ns["cumple_sla"](ns["retraso"], 4) - 89.3) < 0.11, "El 89,3 % llega con 4 días o menos de retraso."


def test_media_ponderada(ns):
    """La conversión global de Madrid y Andalucía es 4,880 %, no la media simple (5,132 %)"""
    r = ns["media_ponderada"]([7.881, 2.383], [149907, 180170])
    assert abs(r - 4.880) < 0.002, f"Media ponderada: {r}"
    assert abs(r - (7.881 + 2.383) / 2) > 0.1, "Has calculado la media simple: pondera por el tamaño."


def test_hidden_serie_pequena(ns):
    """Serie pequeña con valores conocidos (test oculto)"""
    x = pd.Series([-1, 0, 0, 1, 10])
    r = ns["resumen_retrasos"](x)
    assert r["media"] == 2.0 and r["mediana"] == 0.0 and r["n"] == 5, f"Resumen: {r}"
    assert abs(r["desviacion"] - 4.53) < 0.006, f"Desviación muestral: {r['desviacion']}"
    assert ns["cumple_sla"](x, 0) == 60.0
    assert ns["media_ponderada"]([10, 20], [1, 3]) == 17.5
