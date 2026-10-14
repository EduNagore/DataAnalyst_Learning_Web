import numpy as np
import pytest
from analysis import cuped_adjust, diff_in_means, holm_adjust, sample_size_two_proportions, srm_pvalue


def test_srm_reparto_correcto_no_alarma():
    assert srm_pvalue([5000, 5000], [0.5, 0.5]) == pytest.approx(1.0)


def test_srm_detecta_desajuste():
    assert srm_pvalue([50_800, 49_200], [0.5, 0.5]) < 0.001


def test_cuped_reduce_la_varianza_sin_cambiar_la_media():
    rng = np.random.default_rng(0)
    x = rng.normal(100, 20, 5000)
    y = 0.8 * x + rng.normal(0, 10, 5000)
    y_adj, theta = cuped_adjust(y, x)
    assert theta == pytest.approx(0.8, abs=0.05)
    assert y_adj.mean() == pytest.approx(y.mean(), abs=1e-9)
    assert y_adj.var() < 0.5 * y.var()


def test_diff_in_means_intervalo_y_pvalor():
    rng = np.random.default_rng(1)
    a = rng.normal(10, 2, 4000)
    b = rng.normal(10.3, 2, 4000)
    r = diff_in_means(a, b)
    assert r["low"] < r["diff"] < r["high"]
    assert r["diff"] == pytest.approx(0.3, abs=0.15)
    assert r["p_value"] < 0.05


def test_tamano_de_muestra_dos_proporciones():
    # 62 % -> 63,5 %: del orden de 16.000 por grupo
    n = sample_size_two_proportions(0.62, 0.015)
    assert 15_000 < n < 17_500


def test_holm_ordena_y_acota():
    adj = holm_adjust([0.01, 0.04, 0.03])
    assert adj == pytest.approx([0.03, 0.06, 0.06])
    assert all(0 <= p <= 1 for p in adj)
