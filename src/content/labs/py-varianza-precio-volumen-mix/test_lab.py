import pandas as pd
from datakit.data import load_table


def _v(ns, desde, hasta):
    return ns["ventas_por_categoria"](load_table("orders"), load_table("order_items"), load_table("products"), desde, hasta)


def test_ventas_por_categoria(ns):
    """Primer semestre de 2025: 249.558 unidades y 20,45 M€; ocho categorías principales"""
    h = _v(ns, "2025-01-01", "2025-06-30")
    assert len(h) == 8 and int(h["unidades"].sum()) == 249558
    assert abs(h["ingresos"].sum() / 1e6 - 20.454) < 0.001
    assert abs(h["precio_medio"].sum() - (h["ingresos"] / h["unidades"]).sum()) < 1e-9


def test_puente_de_ingresos(ns):
    """H1 2026 frente a H1 2025: +16,13 M€ = volumen +17,79 + precio +0,06 + mix −1,72"""
    a, b = _v(ns, "2025-01-01", "2025-06-30"), _v(ns, "2026-01-01", "2026-06-30")
    p = ns["descomponer"](a, b)
    assert abs(p["variacion"] / 1e6 - 16.131) < 0.001
    assert abs(p["volumen"] / 1e6 - 17.792) < 0.002 and abs(p["precio"] / 1e6 - 0.057) < 0.002
    assert abs(p["mix"] / 1e6 + 1.718) < 0.002
    assert abs(p["precio"] + p["volumen"] + p["mix"] - p["variacion"]) < 1e-3, "El puente debe cuadrar."


def test_el_mix_lo_explica_electronica(ns):
    """Electrónica explica el efecto mix negativo (−2,11 M€): la rotura de stock de marzo de 2026"""
    a, b = _v(ns, "2025-01-01", "2025-06-30"), _v(ns, "2026-01-01", "2026-06-30")
    m = ns["mix_por_categoria"](a, b)
    assert abs(m.sum() / 1e6 + 1.718) < 0.002
    assert m.idxmin() == "cat-00" and abs(m["cat-00"] / 1e6 + 2.109) < 0.002


def test_hidden_dos_categorias(ns):
    """Caso a mano: precio +250, volumen 0, mix −500 (test oculto)"""
    base = pd.DataFrame({"unidades": [100, 100], "ingresos": [1000.0, 2000.0]}, index=["A", "B"])
    base["precio_medio"] = base["ingresos"] / base["unidades"]
    act = pd.DataFrame({"unidades": [150, 50], "ingresos": [1650.0, 1100.0]}, index=["A", "B"])
    act["precio_medio"] = act["ingresos"] / act["unidades"]
    p = ns["descomponer"](base, act)
    assert p["variacion"] == -250 and abs(p["precio"] - 250) < 1e-9
    assert abs(p["volumen"]) < 1e-9 and abs(p["mix"] + 500) < 1e-9
    m = ns["mix_por_categoria"](base, act)
    assert abs(m["A"] - 500) < 1e-9 and abs(m["B"] + 1000) < 1e-9
