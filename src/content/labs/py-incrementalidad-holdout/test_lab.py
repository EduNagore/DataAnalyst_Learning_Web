import numpy as np
from datakit.data import load_table


def _s(ns, metrica, variante):
    return ns["serie"](load_table("experiment_metrics"), "exp-social-ads-geo-holdout", metrica, variante)


def test_series(ns):
    """29 días por brazo; ingresos por usuario medios: 39,78 (control) y 42,12 (tratamiento)"""
    c, t = _s(ns, "revenue_per_user", "control"), _s(ns, "revenue_per_user", "tratamiento")
    assert len(c) == len(t) == 29
    assert abs(c.mean() - 39.78) < 0.01 and abs(t.mean() - 42.12) < 0.01


def test_lift_real_frente_a_atribuido(ns):
    """Ingresos por usuario: +5,9 % (IC 3,3 % a 8,5 %); ingresos atribuidos por último clic: +22,6 %"""
    real = ns["lift_holdout"](_s(ns, "revenue_per_user", "tratamiento"), _s(ns, "revenue_per_user", "control"))
    assert abs(real["lift"] - 0.0590) < 0.001
    assert abs(real["ic_bajo"] - 0.0329) < 0.002 and abs(real["ic_alto"] - 0.0850) < 0.002
    assert real["p"] < 1e-3
    m = "last_click_attributed_revenue_per_user"
    atrib = ns["lift_holdout"](_s(ns, m, "tratamiento"), _s(ns, m, "control"))
    assert abs(atrib["lift"] - 0.2257) < 0.001
    assert atrib["ic_bajo"] > real["ic_alto"], "La atribución cae fuera del IC del efecto causal."


def test_fraccion_incremental(ns):
    """Solo ≈ 26 % del lift atribuido es incremental"""
    assert abs(ns["fraccion_incremental"](0.059, 0.2257) - 0.2614) < 0.001


def test_hidden_holdout_pequeno(ns):
    """Efecto conocido en datos construidos a mano y iROAS (test oculto)"""
    control = np.array([10.0, 11.0, 9.0, 10.0, 10.0])
    trat = control * 1.2
    r = ns["lift_holdout"](trat, control)
    assert abs(r["lift"] - 0.2) < 1e-9 and r["ic_bajo"] < 0.2 < r["ic_alto"]
    assert abs(ns["iroas"](30000, 100000) - 0.3) < 1e-12
