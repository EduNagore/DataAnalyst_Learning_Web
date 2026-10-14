import numpy as np
import pandas as pd
from datakit.data import load_table


def _serie(ns):
    return ns["serie_mensual"](
        load_table("orders"), load_table("order_items"), load_table("customers"), load_table("products")
    )


def test_serie_mensual(ns):
    """Hay una fila por mes y los ingresos de Andalucía en marzo de 2025 superan los 330.000 €"""
    s = _serie(ns)
    assert list(s.columns) == ["rev_and", "rev_resto", "q_and", "q_resto"], f"Columnas: {list(s.columns)}"
    assert s.index.is_monotonic_increasing and "2025-03" in s.index
    assert abs(s.loc["2025-03", "rev_and"] - 336826.5) < 5, f"{s.loc['2025-03', 'rev_and']:.1f}"
    assert abs(s.loc["2025-03", "q_resto"] - 4237) < 1


def test_did_ingresos_y_unidades(ns):
    """Ingresos: +13,9 % (IC +6,4 % a +21,8 %). Unidades: +2,3 % (IC −4,8 % a +9,9 %)"""
    s = _serie(ns)
    r = ns["did_log"](s, "rev")
    assert abs(r["did"] - 0.1298) < 0.002 and abs(r["efecto_pct"] - 13.86) < 0.2
    assert abs(r["se"] - 0.0327) < 0.002
    assert abs(r["ic_inf"] - 6.4) < 0.4 and abs(r["ic_sup"] - 21.8) < 0.5
    q = ns["did_log"](s, "q")
    assert abs(q["efecto_pct"] - 2.26) < 0.2 and q["ic_inf"] < 0 < q["ic_sup"], f"Unidades: {q}"


def test_tendencia_previa_y_evento(ns):
    """Pendiente previa 0,0074 ± 0,0066 (p = 0,29); el estudio de eventos vale 0 en el mes base"""
    s = _serie(ns)
    pend, se, p = ns["pendiente_previa"](s, "rev")
    assert abs(pend - 0.0074) < 0.001 and abs(se - 0.0066) < 0.001 and abs(p - 0.287) < 0.02
    ev = ns["estudio_eventos"](s, "rev")
    assert ev.loc["2025-02"] == 0 and abs(ev.loc["2025-05"] - 0.354) < 0.01


def test_hidden_serie_sintetica(ns):
    """Un efecto conocido en una serie sintética se recupera y sin efecto el DiD es ≈ 0 (test oculto)"""
    meses = pd.period_range("2024-03", "2026-02", freq="M").astype(str)
    rng = np.random.default_rng(0)
    base = 1000 * np.exp(0.02 * np.arange(len(meses)))
    resto = base * np.exp(rng.normal(0, 0.01, len(meses)))
    efecto = np.where(np.arange(len(meses)) >= 12, 1.2, 1.0)
    andalucia = 0.2 * base * efecto * np.exp(rng.normal(0, 0.01, len(meses)))
    s = pd.DataFrame({"rev_and": andalucia, "rev_resto": resto, "q_and": andalucia, "q_resto": resto}, index=meses)
    r = ns["did_log"](s, "rev")
    assert abs(r["efecto_pct"] - 20.0) < 2.0 and r["ic_inf"] < 20 < r["ic_sup"]
    s["rev_and"] = andalucia / efecto
    assert abs(ns["did_log"](s, "rev")["efecto_pct"]) < 2.0
    assert abs(ns["did_log"](s, "rev", previo=("2024-03", "2024-08"), posterior=("2025-09", "2026-02"))["did"]) < 0.05
