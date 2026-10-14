import pandas as pd
from datakit.data import load_table


def _wf(ns):
    return ns["mrr_mensual"](load_table("subscriptions"))


def test_cascada_de_mrr(ns):
    """Mayo de 2026: MRR 202.177 € = 201.592 + 10.864 nuevo − 10.278 churn; 11.448 suscripciones"""
    wf = _wf(ns)
    m = wf.loc[pd.Period("2026-05", "M")]
    assert abs(m["mrr"] - 202177) < 1 and abs(m["mrr_inicial"] - 201592) < 1
    assert abs(m["nuevo"] - 10864) < 1 and abs(m["churn"] - 10278) < 1
    assert m["suscripciones"] == 11448 and m["bajas"] == 578
    assert ((wf["mrr_inicial"] + wf["nuevo"] - wf["churn"] - wf["mrr"]).abs() < 1e-6).all(), "La cascada debe cuadrar."


def test_churn_y_ratio_rapido(ns):
    """Mayo de 2026: churn de MRR 5,10 % y ratio rápido 1,06; ARR ≈ 2,43 M€"""
    wf = _wf(ns).loc[:"2026-05"]
    mayo = pd.Period("2026-05", "M")
    assert abs(ns["churn_de_ingresos"](wf).loc[mayo] - 5.10) < 0.01
    assert abs(ns["ratio_rapido_mrr"](wf).loc[mayo] - 1.057) < 0.005
    assert abs(12 * wf.loc[mayo, "mrr"] / 1e6 - 2.426) < 0.001


def test_retencion_a_12_meses(ns):
    """De cada 100 € de MRR activo en mayo de 2025, siguen 55,8 € un año después (GRR = NRR: no hay ampliaciones)"""
    r = ns["retencion_de_ingresos"](load_table("subscriptions"), "2025-05-31", "2026-05-31")
    assert abs(r["grr"] - 55.85) < 0.05 and r["nrr"] == r["grr"] and abs(r["logos"] - 55.85) < 0.05


def test_hidden_cascada_pequena(ns):
    """Tres suscripciones a mano: altas, bajas y retención (test oculto)"""
    subs = pd.DataFrame(
        {
            "subscription_id": ["a", "b", "c"],
            "plan": ["mensual", "mensual", "anual"],
            "started_at": pd.to_datetime(["2025-01-10", "2025-01-20", "2025-02-05"]),
            "cancelled_at": pd.to_datetime(["2025-02-28", None, None]),
            "mrr_eur": [10.0, 20.0, 30.0],
        }
    )
    wf = ns["mrr_mensual"](subs)
    ene, feb = (wf.loc[pd.Period(m, "M")] for m in ("2025-01", "2025-02"))
    assert (ene["mrr_inicial"], ene["nuevo"], ene["churn"], ene["mrr"]) == (0, 30, 0, 30)
    assert (feb["mrr_inicial"], feb["nuevo"], feb["churn"], feb["mrr"]) == (30, 30, 10, 50), "Baja el último día del mes: cuenta como churn de ese mes."
    r = ns["retencion_de_ingresos"](subs, "2025-02-28", "2025-03-31")
    assert abs(r["grr"] - 100) < 1e-9 and abs(r["logos"] - 100) < 1e-9
    r2 = ns["retencion_de_ingresos"](subs, "2025-01-31", "2025-03-31")
    assert abs(r2["grr"] - 100 * 20 / 30) < 1e-9 and abs(r2["logos"] - 50) < 1e-9
