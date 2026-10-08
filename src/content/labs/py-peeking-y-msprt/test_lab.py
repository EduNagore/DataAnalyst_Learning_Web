import numpy as np
from datakit.data import load_table


def test_peeking_infla_los_falsos_positivos(ns):
    """1 revisión ≈ 5 %; 2 ≈ 8,4 %; 10 ≈ 19 %"""
    assert abs(ns["simular_peeking"](1, n_sim=30000, seed=1) - 0.05) < 0.007
    assert abs(ns["simular_peeking"](2, n_sim=30000, seed=1) - 0.084) < 0.01
    assert abs(ns["simular_peeking"](10, n_sim=30000, seed=1) - 0.193) < 0.012


def test_limites_secuenciales(ns):
    """Con límites O'Brien-Fleming (c = 2,041, K = 5) la tasa vuelve a ≈ 5 %"""
    lim = ns["limites_obf"](5, 2.041)
    assert np.allclose(lim, [4.5637, 3.2272, 2.6349, 2.2819, 2.041], atol=0.01), f"Límites: {np.round(lim, 3)}"
    assert abs(ns["simular_peeking"](5, n_sim=40000, seed=2, limites=lim) - 0.05) < 0.01


def test_msprt(ns):
    """Sin efecto, el mSPRT vigilado en cada observación no supera el 5 %; con efecto casi siempre rechaza"""
    nulo = ns["simular_msprt"](n_obs=2000, n_sim=3000, seed=3)
    assert nulo < 0.06, f"Falsos positivos del mSPRT: {nulo:.3f}"
    assert ns["simular_msprt"](n_obs=2000, n_sim=500, efecto=0.15, seed=3) > 0.95


def test_primer_cruce_en_experimentos_reales(ns):
    """El checkout cruza p < 0,05 el día 7 (efecto real); exp-generic-02 lo cruza el día 5 y acaba con p = 0,54"""
    m, e = load_table("experiment_metrics"), load_table("experiments")
    resultado = {}
    for _, fila in e.iterrows():
        x = m[(m["experiment_id"] == fila["experiment_id"]) & (m["metric_name"] == fila["primary_metric"])].sort_values("date")
        c = x.loc[x["variant"] == "control", "value"].to_numpy()
        t = x.loc[x["variant"] == "tratamiento", "value"].to_numpy()
        resultado[fila["experiment_id"]] = ns["primer_cruce"](c, t)
    assert resultado["exp-checkout-v2"] == 7 and resultado["exp-social-ads-geo-holdout"] == 7
    assert resultado["exp-generic-02"] == 5
    cruzan = [k for k, v in resultado.items() if v is not None]
    assert sorted(cruzan) == ["exp-checkout-v2", "exp-generic-02", "exp-social-ads-geo-holdout"]


def test_hidden_casos_borde(ns):
    """Series cortas, mínimo mayor que la longitud y reproducibilidad (test oculto)"""
    assert ns["primer_cruce"]([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], minimo=5) is None
    a = np.arange(10.0)
    assert ns["primer_cruce"](a, a + 100.0, minimo=3) == 3
    assert ns["simular_peeking"](4, n_sim=500, seed=7) == ns["simular_peeking"](4, n_sim=500, seed=7)
    assert ns["simular_peeking"](10, n_sim=3000, seed=1) > ns["simular_peeking"](2, n_sim=3000, seed=1)
    assert ns["simular_msprt"](n_obs=200, n_sim=100, seed=4) == ns["simular_msprt"](n_obs=200, n_sim=100, seed=4)
    assert ns["simular_msprt"](n_obs=200, n_sim=300, tau2=0.5, alpha=0.01, seed=1) <= 0.02
