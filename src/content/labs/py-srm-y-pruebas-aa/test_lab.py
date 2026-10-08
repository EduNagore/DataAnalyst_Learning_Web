import pandas as pd
from datakit.data import load_table


def test_chi2_del_motor_de_recomendaciones(ns):
    """11.166 frente a 8.834 con reparto 50/50: χ² = 271,9 y p ≈ 0"""
    chi2, p = ns["srm_chi2"](11166, 8834)
    assert abs(chi2 - 271.9112) < 0.01, f"χ² = {chi2:.4f}"
    assert p < 1e-50


def test_reparto_distinto_del_5050(ns):
    """Con un diseño 90/10, 9.000/1.000 es perfecto y 8.700/1.300 es un SRM"""
    chi2, p = ns["srm_chi2"](9000, 1000, reparto=(0.9, 0.1))
    assert chi2 == 0 and p == 1
    assert ns["srm_chi2"](8700, 1300, reparto=(0.9, 0.1))[1] < 0.001


def test_tabla_de_experimentos(ns):
    """15 experimentos; solo exp-reco-engine es SRM; el siguiente es exp-generic-02 con p = 0,053"""
    t = ns["srm_todos"](load_table("experiment_assignments"))
    assert list(t.columns) == ["experiment_id", "control", "tratamiento", "pct_tratamiento", "chi2", "p", "srm"]
    assert len(t) == 15 and t["p"].is_monotonic_increasing
    assert t["srm"].sum() == 1 and t.iloc[0]["experiment_id"] == "exp-reco-engine" and bool(t.iloc[0]["srm"])
    assert abs(t.iloc[0]["pct_tratamiento"] - 44.17) < 0.01
    assert t.iloc[1]["experiment_id"] == "exp-generic-02" and abs(t.iloc[1]["p"] - 0.0527) < 0.001


def test_hidden_simulacion_aa(ns):
    """En A/A: ≈ 5 % de significativos y ≈ 0,1 % de SRM; con el umbral por defecto del SRM no se aplica a todo (test oculto)"""
    r = ns["simular_aa"](n_exp=6000, n_por_rama=5000, seed=3)
    assert abs(r["signif_05"] - 0.05) < 0.012, f"Falsos positivos: {r['signif_05']:.4f}"
    assert r["srm_001"] < 0.004, f"SRM: {r['srm_001']:.4f}"
    assert ns["simular_aa"](n_exp=500, seed=1) == ns["simular_aa"](n_exp=500, seed=1)
    df = pd.DataFrame({"experiment_id": ["a"] * 100, "variant": ["control"] * 55 + ["tratamiento"] * 45})
    estricto = ns["srm_todos"](df, umbral=0.001)
    laxo = ns["srm_todos"](df, umbral=0.5)
    assert not bool(estricto.iloc[0]["srm"]) and bool(laxo.iloc[0]["srm"])
