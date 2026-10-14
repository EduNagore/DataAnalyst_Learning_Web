import numpy as np
import pandas as pd
import pytest
from did import did_estimate, synthetic_control_weights


def _panel(effect=0.10):
    meses = pd.date_range("2024-01-01", periods=12, freq="MS")
    filas = []
    for region, base in [("T", 100.0), ("C1", 80.0), ("C2", 120.0)]:
        for i, mes in enumerate(meses):
            valor = base * (1 + 0.01 * i)
            if region == "T" and mes >= pd.Timestamp("2024-07-01"):
                valor *= 1 + effect
            filas.append({"region": region, "mes": mes, "ingresos": valor, "unidades": valor / 10})
    return pd.DataFrame(filas)


def test_did_recupera_el_efecto_conocido():
    r = did_estimate(_panel(0.10), "T", "2024-07-01")
    assert r["effect_pct"] == pytest.approx(0.10, abs=0.01)


def test_did_sin_efecto_da_cero():
    r = did_estimate(_panel(0.0), "T", "2024-07-01")
    assert r["effect_pct"] == pytest.approx(0.0, abs=0.005)


def test_pesos_sinteticos_son_validos():
    rng = np.random.default_rng(0)
    controles = rng.normal(100, 10, size=(24, 4))
    verdadero = np.array([0.5, 0.3, 0.2, 0.0])
    tratada = controles @ verdadero
    w = synthetic_control_weights(tratada, controles)
    assert w.sum() == pytest.approx(1.0, abs=1e-6)
    assert (w >= -1e-9).all()
    assert w == pytest.approx(verdadero, abs=0.05)
