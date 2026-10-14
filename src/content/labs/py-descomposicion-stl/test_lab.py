import numpy as np
import pandas as pd
from datakit.data import load_table


def _res(ns):
    serie = ns["pedidos_diarios"](load_table("orders"))
    return serie, ns["descomponer"](serie)


def test_serie_y_crecimiento(ns):
    """912 días desde 2024-01-01 y crecimiento mensual de la tendencia del 6,2 %"""
    serie, res = _res(ns)
    assert len(serie) == 912 and serie.index.freq is not None and serie.index[0] == pd.Timestamp("2024-01-01")
    assert abs(serie.sum() - 359548) < 5
    assert abs(100 * ns["crecimiento_mensual"](res) - 6.22) < 0.1


def test_semana_y_sigma(ns):
    """Viernes ≈ 1,049 y sábado ≈ 1,043; domingo ≈ 0,955; sigma robusto ≈ 0,047"""
    _, res = _res(ns)
    f = ns["factores_semanales"](res)
    assert list(f.index) == list(range(7))
    assert abs(f[4] - 1.049) < 0.01 and abs(f[5] - 1.043) < 0.01 and abs(f[6] - 0.955) < 0.01
    assert abs(ns["sigma_robusto"](res) - 0.0469) < 0.003


def test_dias_especiales(ns):
    """Black Friday +16,9 %, Navidad +10,3 % y festivos nacionales −11,1 % de pedidos"""
    _, res = _res(ns)
    e = ns["efecto_dias_especiales"](res, load_table("calendar"))
    assert set(e) == {"black_friday", "navidad", "festivo_nacional"}
    assert abs(e["black_friday"] - 16.9) < 1.0 and abs(e["navidad"] - 10.3) < 1.0 and abs(e["festivo_nacional"] + 11.1) < 1.0


def test_hidden_serie_sintetica(ns):
    """STL recupera una semana y un crecimiento conocidos (test oculto)"""
    rng = np.random.default_rng(0)
    idx = pd.date_range("2024-01-01", periods=400, freq="D")
    semana = np.array([0.0, 0.0, 0.0, 0.0, 0.2, 0.2, -0.3])
    log = np.log(100) + 0.002 * np.arange(400) + semana[idx.dayofweek] + rng.normal(0, 0.02, 400)
    serie = pd.Series(np.exp(log), index=idx)
    res = ns["descomponer"](serie)
    assert abs(100 * ns["crecimiento_mensual"](res) - 100 * (np.exp(0.002 * 30) - 1)) < 0.5
    f = ns["factores_semanales"](res)
    assert f[4] > f[0] > f[6] and abs(f[6] / f[0] - np.exp(-0.3)) < 0.03
    assert ns["sigma_robusto"](res) < 0.05
    orders = pd.DataFrame(
        {
            "order_id": ["a", "b", "c", "d"],
            "order_date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-03", "2024-01-03"]),
            "status": ["completado", "cancelado", "completado", "completado"],
        }
    )
    s = ns["pedidos_diarios"](orders, desde="2024-01-01")
    assert list(s.values) == [1.0, 0.0, 2.0], "Cuenta pedidos no cancelados y rellena los días vacíos con 0."
