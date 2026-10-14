import numpy as np
import pandas as pd
from datakit.data import load_table


def _serie(ns):
    return ns["pedidos_diarios"](load_table("orders"))


def test_metricas(ns):
    """Métricas a mano: error de 10 en todos los puntos, escala 5 y un pronóstico sesgado a la baja"""
    m = ns["metricas"]([100, 200, 100, 200], [90, 190, 90, 190], 5.0)
    assert abs(m["mae"] - 10) < 1e-9 and abs(m["rmse"] - 10) < 1e-9 and abs(m["mase"] - 2) < 1e-9
    assert abs(m["mape"] - 100 * np.mean([0.1, 0.05, 0.1, 0.05])) < 1e-9
    assert abs(m["sesgo_pct"] - 100 * (560 / 600 - 1)) < 1e-9


def test_metodos_simples(ns):
    """Naive estacional repite la última semana; con crecimiento 0 % es idéntico"""
    idx = pd.date_range("2024-01-01", periods=70, freq="D")
    train = pd.Series(np.tile(np.arange(1.0, 8.0), 10), index=idx)
    p = ns["pronostico_snaive"](train, 10)
    assert list(p[:7]) == [1, 2, 3, 4, 5, 6, 7] and p[7] == 1
    assert np.allclose(ns["pronostico_snaive_deriva"](train, 10), p), "Con serie estable el crecimiento es 1."
    creciente = pd.Series(np.tile(np.arange(1.0, 8.0), 10) * np.repeat(1.01 ** np.arange(10), 7), index=idx)
    assert ns["pronostico_snaive_deriva"](creciente, 7).sum() > ns["pronostico_snaive"](creciente, 7).sum()
    hw = ns["pronostico_holt_winters"](train, 14)
    assert hw.shape == (14,) and np.all(hw > 0) and np.abs(hw[:7] - np.arange(1.0, 8.0)).max() < 0.5


def test_backtest_y_ranking(ns):
    """19 orígenes; Holt-Winters: MAE ≈ 37,2, MAPE ≈ 7,5 %; naive estacional: MAE ≈ 43,3; con crecimiento: ≈ 53,4"""
    s = _serie(ns)
    hw = ns["backtest"](s, ns["pronostico_holt_winters"])
    sn = ns["backtest"](s, ns["pronostico_snaive"])
    cr = ns["backtest"](s, ns["pronostico_snaive_deriva"])
    assert len(hw) == 19 and hw.index[0] == pd.Timestamp("2025-01-01") and hw.index[-1] == pd.Timestamp("2026-05-20")
    assert abs(hw["mae"].mean() - 37.25) < 1.0 and abs(hw["mape"].mean() - 7.46) < 0.3 and abs(hw["mase"].mean() - 1.50) < 0.05
    assert abs(sn["mae"].mean() - 43.3) < 0.5 and abs(cr["mae"].mean() - 53.4) < 0.8
    assert hw["mae"].mean() < sn["mae"].mean() < cr["mae"].mean()


def test_hidden_origen_movil_sin_fuga(ns):
    """El backtest no usa datos del periodo de prueba y termina cuando no cabe otro horizonte completo (test oculto)"""
    idx = pd.date_range("2024-01-01", periods=100, freq="D")
    serie = pd.Series(np.arange(100.0) + 10, index=idx)
    vistos = []

    def espia(train, h):
        vistos.append((train.index[-1], len(train)))
        return np.full(h, train.iloc[-1])

    b = ns["backtest"](serie, espia, h=10, inicio="2024-02-01", paso=10)
    assert all(ultimo < origen for (ultimo, _), origen in zip(vistos, b.index, strict=True))
    assert b.index[-1] + pd.Timedelta(days=9) <= serie.index[-1]
    assert len(b) >= 5
    assert (b["sesgo_pct"] < 0).all(), "Repetir el último valor en una serie creciente sesga a la baja."
