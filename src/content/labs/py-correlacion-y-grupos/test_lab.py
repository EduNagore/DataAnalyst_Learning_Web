import pandas as pd
from datakit.testing import assert_columns, assert_frame_equivalent


def test_correlaciones(ns):
    """Pearson 0,473 y Spearman 0,625 entre líneas e importe"""
    r = ns["correlaciones"](ns["pedidos"], "lineas", "importe")
    assert set(r) == {"pearson", "spearman"}, f"Claves: {sorted(r)}"
    assert abs(r["pearson"] - 0.473) < 0.0015, f"Pearson: {r['pearson']}"
    assert abs(r["spearman"] - 0.625) < 0.0015, f"Spearman: {r['spearman']}"


def test_resumen_por_segmento(ns):
    """El ticket medio es ≈ 301-302 € en todos los segmentos"""
    r = ns["resumen_por_grupo"](ns["pedidos"], "segment", "importe")
    assert_columns(r, ["segment", "n", "media", "mediana"])
    medias = dict(zip(r["segment"], r["media"], strict=True))
    esperado = {"habitual": 302.0, "nuevo": 301.9, "ocasional": 301.4, "vip": 301.5}
    for seg, m in esperado.items():
        assert abs(medias[seg] - m) < 0.11, f"Segmento {seg}: media {medias.get(seg)} (esperada {m})"
    assert list(r["segment"]) == sorted(r["segment"]), "Ordena por el grupo."


def test_importe_bruto(ns):
    """El importe bruto (importe ÷ (1 − descuento)) es casi constante: relación mecánica"""
    r = ns["importe_bruto_por_descuento"](ns["pedidos"])
    assert_columns(r, ["discount_pct", "pedidos", "importe_medio", "importe_bruto_medio"])
    esperado = pd.DataFrame(
        {
            "discount_pct": [0.0, 0.05, 0.10, 0.15, 0.20, 0.30],
            "importe_medio": [334.3, 317.8, 303.5, 284.5, 271.4, 240.4],
            "importe_bruto_medio": [334.3, 334.5, 337.3, 334.7, 339.3, 343.4],
        }
    )
    assert_frame_equivalent(r[list(esperado.columns)], esperado, sort_by=["discount_pct"], tol=0.11)
    assert r["importe_bruto_medio"].max() - r["importe_bruto_medio"].min() < 10, "El bruto debería ser casi constante."


def test_no_modifica_la_entrada(ns):
    """No modifica el DataFrame de entrada"""
    df = ns["pedidos"]
    antes = df.copy()
    ns["resumen_por_grupo"](df, "segment", "importe")
    ns["importe_bruto_por_descuento"](df)
    assert df.equals(antes), "Has modificado `pedidos`. Trabaja con copias."


def test_hidden_tabla_pequena(ns):
    """Tabla pequeña con correlación perfecta y grupos desiguales (test oculto)"""
    df = pd.DataFrame(
        {
            "g": ["b", "a", "a", "b", "a"],
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 30, 40, 50],
            "order_id": list("12345"),
            "discount_pct": [0.0, 0.5, 0.5, 0.0, 0.5],
            "importe": [100.0, 50.0, 50.0, 100.0, 50.0],
        }
    )
    c = ns["correlaciones"](df, "x", "y")
    assert c == {"pearson": 1.0, "spearman": 1.0}, f"Correlaciones: {c}"
    r = ns["resumen_por_grupo"](df, "g", "y").set_index("g")
    assert r.loc["a", "n"] == 3 and r.loc["b", "n"] == 2 and r.loc["a", "mediana"] == 30.0, f"Resumen: {r.to_dict()}"
    b = ns["importe_bruto_por_descuento"](df).set_index("discount_pct")
    assert b.loc[0.5, "importe_bruto_medio"] == 100.0 and b.loc[0.0, "importe_bruto_medio"] == 100.0, f"Bruto: {b.to_dict()}"
