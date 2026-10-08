import pandas as pd
from datakit.testing import assert_columns


def test_serie_completa(ns):
    """La serie completa tiene 42 meses (enero de 2023 a junio de 2026) sin huecos"""
    c = ns["completar_meses"](ns["mensual"])
    assert len(c) == 42, f"Se esperaban 42 meses y hay {len(c)}."
    pasos = c["mes"].diff().dropna().dt.days
    assert pasos.between(28, 31).all(), "Los meses deben ser consecutivos."


def test_comparaciones_de_2026(ns):
    """Marzo de 2026: YoY +36,3 %; junio de 2026: YTD 36,59 M€ y 12 meses móviles 65,59 M€"""
    c = ns["con_comparaciones"](ns["mensual"])
    assert_columns(c, ["mes", "ingresos", "ytd", "py", "yoy_pct", "movil_12m"])
    fila = lambda a, m: c[(c["mes"].dt.year == a) & (c["mes"].dt.month == m)].iloc[0]  # noqa: E731
    assert abs(fila(2026, 3)["yoy_pct"] - 36.3) < 0.11, f"YoY de marzo: {fila(2026, 3)['yoy_pct']}"
    assert abs(fila(2026, 2)["yoy_pct"] - 88.7) < 0.11
    assert abs(fila(2026, 6)["ytd"] - 36585357.5) < 2, f"YTD junio 2026: {fila(2026, 6)['ytd']}"
    assert abs(fila(2026, 6)["movil_12m"] - 65591640.6) < 2


def test_ytd_justo(ns):
    """El YTD de junio de 2026 supera en un 78,9 % al de junio de 2025 (comparación justa)"""
    a, b = ns["ytd_hasta"](ns["mensual"], 2026, 6), ns["ytd_hasta"](ns["mensual"], 2025, 6)
    assert abs(b - 20454474) < 2, f"YTD junio 2025: {b}"
    assert abs((a / b - 1) * 100 - 78.9) < 0.11


def test_hidden_serie_con_hueco(ns):
    """Con un mes ausente, el hueco se rellena con 0 y el mismo mes del año anterior sigue alineado (test oculto)"""
    meses = list(pd.date_range("2024-01-01", periods=14, freq="MS"))
    del meses[5]  # falta junio de 2024
    df = pd.DataFrame({"mes": meses, "ingresos": [100.0] * len(meses)})
    c = ns["con_comparaciones"](df)
    assert len(c) == 14, "Debe haber 14 meses tras completar el hueco."
    assert c.loc[c["mes"] == "2024-06-01", "ingresos"].iloc[0] == 0.0
    f = c[c["mes"] == "2025-02-01"].iloc[0]
    assert f["py"] == 100.0 and f["yoy_pct"] == 0.0, f"Febrero de 2025 frente a febrero de 2024: {f.to_dict()}"
    g = c[c["mes"] == "2025-02-01"].iloc[0]
    assert abs(g["movil_12m"] - 1100.0) < 1e-9, "Los 12 meses móviles incluyen un mes a 0."
