import numpy as np
from datakit.data import load_table


def test_correcciones_contra_valores_de_referencia(ns):
    """Valores calculados con statsmodels.multipletests para p = [0,01, 0,04, 0,03, 0,005]"""
    p = [0.01, 0.04, 0.03, 0.005]
    assert np.allclose(ns["ajustar_bonferroni"](p), [0.04, 0.16, 0.12, 0.02])
    assert np.allclose(ns["ajustar_holm"](p), [0.03, 0.06, 0.06, 0.02])
    assert np.allclose(ns["ajustar_bh"](p), [0.02, 0.04, 0.04, 0.02])


def test_parejas_de_transportistas(ns):
    """10 parejas; la de menor p es CorreosExpress–SEUR (p = 0,0022; Holm y BH = 0,0215)"""
    t = ns["comparar_transportistas"](load_table("shipments"))
    assert list(t.columns) == ["a", "b", "dif_media", "p", "p_holm", "p_bh"], f"Columnas: {list(t.columns)}"
    assert len(t) == 10 and t["p"].is_monotonic_increasing
    primera = t.iloc[0]
    assert {primera["a"], primera["b"]} == {"CorreosExpress", "SEUR"}
    assert abs(primera["p"] - 0.00215) < 0.0002
    assert abs(primera["p_holm"] - 0.0215) < 0.002 and abs(primera["p_bh"] - 0.0215) < 0.002
    assert abs(abs(primera["dif_media"]) - 0.0245) < 0.001
    assert (t["p"] < 0.05).sum() == 3 and (t["p_holm"] < 0.05).sum() == 1


def test_simulacion_fwer(ns):
    """Con 20 nulas: ≈ 64 % sin corregir y ≈ 5 % con Bonferroni o BH"""
    r = ns["simular_fwer"](20, n_sim=2000, seed=1)
    assert set(r) == {"sin_correccion", "bonferroni", "bh"}, f"Claves: {sorted(r)}"
    assert abs(r["sin_correccion"] - 0.642) < 0.04, f"Sin corrección: {r['sin_correccion']:.3f}"
    assert r["bonferroni"] < 0.09 and r["bh"] < 0.09


def test_hidden_propiedades(ns):
    """Monotonía, orden, límites y relación entre métodos (test oculto)"""
    rng = np.random.default_rng(3)
    p = rng.random(30) ** 3  # muchos pequeños
    b, h, q = ns["ajustar_bonferroni"](p), ns["ajustar_holm"](p), ns["ajustar_bh"](p)
    assert (p <= h + 1e-12).all() and (h <= b + 1e-12).all(), "p ≤ Holm ≤ Bonferroni"
    assert (q <= b + 1e-12).all() and (q >= p - 1e-12).all()
    assert b.max() <= 1 and h.max() <= 1 and q.max() <= 1
    # monotonía: el orden de los p-valores se conserva tras el ajuste
    orden = np.argsort(p)
    assert np.all(np.diff(h[orden]) >= -1e-12) and np.all(np.diff(q[orden]) >= -1e-12)
    # el ajuste de un único p-valor es la identidad
    assert np.allclose(ns["ajustar_holm"]([0.03]), [0.03]) and np.allclose(ns["ajustar_bh"]([0.03]), [0.03])
    # no se modifica la entrada
    entrada = np.array([0.2, 0.01, 0.5])
    copia = entrada.copy()
    ns["ajustar_holm"](entrada)
    ns["ajustar_bh"](entrada)
    assert np.array_equal(entrada, copia)
    assert ns["simular_fwer"](5, n_sim=300, seed=2) == ns["simular_fwer"](5, n_sim=300, seed=2)
