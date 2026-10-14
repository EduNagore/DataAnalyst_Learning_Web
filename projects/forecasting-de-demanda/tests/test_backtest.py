import numpy as np
import pandas as pd
import pytest
from backtest import backtest, bias, interval_coverage, rolling_origins, seasonal_naive, wape


def test_ingenuo_estacional_repite_la_semana():
    y = pd.Series(np.arange(1, 15, dtype=float))
    f = seasonal_naive(y, 10, season=7)
    assert list(f[:7]) == list(range(8, 15))
    assert list(f[7:]) == [8, 9, 10]


def test_origenes_moviles():
    origins = rolling_origins(n=100, horizon=10, n_origins=4, min_train=30)
    assert origins == [60, 70, 80, 90]
    assert all(o >= 30 for o in origins)


def test_metricas():
    y = np.array([10.0, 20.0, 30.0])
    f = np.array([12.0, 18.0, 33.0])
    assert wape(y, f) == pytest.approx(7 / 60)
    assert bias(y, f) == pytest.approx(3 / 60)
    assert interval_coverage(y, f - 3, f + 3) == pytest.approx(1.0)
    assert interval_coverage(y, f - 1, f + 1) == pytest.approx(0.0)


def test_backtest_no_ve_el_futuro():
    vistos = []

    def modelo(historia: pd.Series, horizonte: int) -> np.ndarray:
        vistos.append(len(historia))
        return np.full(horizonte, historia.iloc[-1])

    serie = pd.Series(np.arange(100, dtype=float))
    res = backtest(serie, modelo, horizon=10, n_origins=4, min_train=30)
    assert vistos == [60, 70, 80, 90]
    assert len(res) == 4
    assert {"wape", "bias"} <= set(res.columns)
