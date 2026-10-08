import numpy as np


def test_error_estandar_teorico(ns):
    """σ/√n vale 162,68 (n = 5), 66,41 (n = 30) y 25,72 (n = 200)"""
    x = ns["importes"]
    assert abs(ns["error_estandar_teorico"](x, 5) - 162.68) < 0.05
    assert abs(ns["error_estandar_teorico"](x, 30) - 66.41) < 0.05
    assert abs(ns["error_estandar_teorico"](x, 200) - 25.72) < 0.05


def test_medias_muestrales(ns):
    """Las medias están centradas en 301,7 € y su desviación se parece al error estándar teórico"""
    x = ns["importes"]
    m = ns["medias_muestrales"](x, 30, 8000, 11)
    assert len(m) == 8000, f"Se esperaban 8.000 medias y hay {len(m)}."
    assert abs(m.mean() - x.mean()) < 4, f"Media de las medias: {m.mean():.1f}"
    assert abs(m.std() / ns["error_estandar_teorico"](x, 30) - 1) < 0.05, f"Desviación de las medias: {m.std():.1f}"


def test_es_reproducible(ns):
    """Con la misma semilla se obtienen las mismas medias"""
    a = ns["medias_muestrales"](ns["importes"], 10, 50, 5)
    b = ns["medias_muestrales"](ns["importes"], 10, 50, 5)
    assert np.array_equal(a, b), "Usa np.random.default_rng(seed) para que el resultado sea reproducible."


def test_cobertura(ns):
    """La cobertura del IC «al 95 %» mejora con n: ≈ 84 % (n = 10), ≈ 90 % (n = 30), ≈ 94 % (n = 200)"""
    x = ns["importes"]
    c10 = ns["cobertura_ic"](x, 10, 4000, 21)
    c30 = ns["cobertura_ic"](x, 30, 4000, 22)
    c200 = ns["cobertura_ic"](x, 200, 3000, 23)
    assert 80.0 <= c10 <= 87.0, f"n = 10: {c10}"
    assert 87.0 <= c30 <= 92.5, f"n = 30: {c30}"
    assert 92.0 <= c200 <= 96.0, f"n = 200: {c200}"
    assert c10 < c30 < c200, "La cobertura debería aumentar con el tamaño de la muestra."


def test_hidden_poblacion_normal(ns):
    """Con una población normal la cobertura ya es ≈ 95 % con n = 30 (test oculto)"""
    rng = np.random.default_rng(99)
    x = rng.normal(50, 10, size=100_000)
    assert abs(ns["error_estandar_teorico"](x, 25) - 2.0) < 0.05
    c = ns["cobertura_ic"](x, 30, 4000, 4)
    assert 93.0 <= c <= 96.5, f"Cobertura con datos normales: {c}"
