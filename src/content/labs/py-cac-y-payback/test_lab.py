import pandas as pd
from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def test_cac_mixto(ns):
    """El CAC mixto es 114,04 € (2023), 78,09 € (2024), 63,50 € (2025) y 52,79 € (2026)"""
    r = ns["cac_por_anio"](load_table("marketing_spend"), load_table("customers"))
    assert_columns(r, ["anio", "gasto", "clientes_nuevos", "cac_mixto"])
    esperado = pd.DataFrame(
        {
            "anio": [2023, 2024, 2025, 2026],
            "gasto": [1258886.0, 1235375.0, 1323437.0, 649353.0],
            "clientes_nuevos": [11039, 15820, 20841, 12300],
            "cac_mixto": [114.04, 78.09, 63.50, 52.79],
        }
    )
    assert_frame_equivalent(r, esperado, sort_by=["anio"], tol=0.51)


def test_cac_por_canal(ns):
    """En 2025 el canal más barato es direct (25,7 €) y el más caro affiliate (163,6 €)"""
    r = ns["cac_por_canal"](load_table("marketing_spend"), load_table("customers"), 2025)
    assert_columns(r, ["channel", "gasto", "clientes_nuevos", "cac"])
    canales = list(r["channel"])
    assert canales[0] == "direct" and canales[-1] == "affiliate", f"Orden de canales: {canales}"
    cac = dict(zip(r["channel"], r["cac"], strict=True))
    assert abs(cac["direct"] - 25.7) < 0.11 and abs(cac["affiliate"] - 163.6) < 0.11, f"CAC por canal: {cac}"


def test_payback(ns):
    """El margen acumulado de la cohorte 2024 cubre 78,09 € en el mes 0 y 400 € en el mes 7"""
    m = ns["margen_mensual"]
    assert ns["payback_meses"](m, 78.09) == 0, "Con CAC 78,09 € el payback es el mes 0."
    assert ns["payback_meses"](m, 400) == 7, "Con CAC 400 € el payback es el mes 7."


def test_hidden_serie_pequena(ns):
    """Serie pequeña: borde (acumulado = CAC) y CAC inalcanzable (test oculto)"""
    m = pd.Series([100.0, 100.0, 50.0, 50.0], index=[0, 1, 2, 3])
    assert ns["payback_meses"](m, 100) == 0
    assert ns["payback_meses"](m, 150) == 1
    assert ns["payback_meses"](m, 300) == 3
    assert ns["payback_meses"](m, 1000) is None
