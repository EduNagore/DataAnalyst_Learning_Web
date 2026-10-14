import numpy as np
import pandas as pd
from datakit.data import load_table


def _panel(ns):
    return ns["panel_regional"](
        load_table("orders"), load_table("order_items"), load_table("customers"), load_table("products")
    )


def _andalucia(panel):
    return next(c for c in panel.columns if c.startswith("Andaluc"))


def test_panel(ns):
    """38 meses (2023-01 a 2026-02) y 16 regiones; sin valores ausentes"""
    p = _panel(ns)
    assert p.shape == (38, 16), f"Forma: {p.shape}"
    assert p.index[0] == "2023-01" and p.index[-1] == "2026-02" and not p.isna().any().any()
    assert abs(p.loc["2025-03", _andalucia(p)] - 336826.5) < 5


def test_pesos_y_efecto(ns):
    """Madrid ≈ 39,5 %, País Vasco ≈ 18,4 %; ajuste previo 4,7 puntos y brecha +13,9 %"""
    p = _panel(ns)
    r = ns["efecto_sintetico"](p, _andalucia(p))
    w = r["pesos"]
    assert abs(w.sum() - 1) < 1e-9 and (w >= 0).all() and _andalucia(p) not in w.index
    assert abs(w["Madrid"] - 0.3945) < 0.01 and abs(w["País Vasco"] - 0.184) < 0.01
    assert abs(r["rmse_previo"] - 4.72) < 0.1 and abs(r["gap_pct"] - 13.93) < 0.3 and abs(r["ratio"] - 11.49) < 0.3


def test_placebos(ns):
    """Andalucía tiene el mayor cociente de 16 regiones (p = 1/16); Aragón es la siguiente (≈ 5,1)"""
    p = _panel(ns)
    pl = ns["placebos"](p, _andalucia(p))
    assert list(pl.columns) == ["region", "ratio", "gap_pct"] and len(pl) == 16
    assert pl["ratio"].is_monotonic_decreasing and pl.iloc[0]["region"] == _andalucia(p)
    assert pl.iloc[1]["region"] == "Aragón" and abs(pl.iloc[1]["ratio"] - 5.11) < 0.2
    assert abs(pl.loc[pl["region"] == "Extremadura", "gap_pct"].iloc[0] - 16.57) < 0.5


def test_hidden_efecto_conocido_en_datos_sinteticos(ns):
    """Con un efecto del +30 % inyectado en una región, el método lo recupera (test oculto)"""
    rng = np.random.default_rng(1)
    meses = pd.period_range("2023-01", "2025-12", freq="M").astype(str)
    t = np.arange(len(meses))
    comun = 100 * np.exp(0.02 * t) * (1 + 0.1 * np.sin(t / 2))
    cols = {f"R{i}": comun * (1 + 0.5 * i) * np.exp(rng.normal(0, 0.01, len(t))) for i in range(8)}
    panel = pd.DataFrame(cols, index=meses)
    panel["TRAT"] = comun * 2 * np.exp(rng.normal(0, 0.01, len(t)))
    panel.loc["2025-01":, "TRAT"] *= 1.3
    r = ns["efecto_sintetico"](panel, "TRAT", inicio="2025-01")
    assert abs(r["gap_pct"] - 30) < 4, f"Brecha: {r['gap_pct']:.1f} %"
    assert r["ratio"] > 5
    pl = ns["placebos"](panel, "TRAT", inicio="2025-01")
    assert pl.iloc[0]["region"] == "TRAT"
    idx = ns["a_indice"](panel, "2024-12")
    assert abs(idx.loc[:"2024-12"].mean().mean() - 100) < 1e-9
