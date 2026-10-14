import numpy as np


def test_estimadores(ns):
    """Efecto verdadero 1,0: ingenuo ≈ 3,06; IPW ≈ 1,03; emparejamiento ≈ 1,02"""
    df = ns["simular_observacional"]()
    assert list(df.columns) == ["x1", "x2", "t", "y"] and len(df) == 20000
    assert abs(df["t"].mean() - 0.5046) < 0.005
    assert abs(ns["diferencia_ingenua"](df) - 3.06) < 0.05
    ps = ns["propension"](df)
    assert ps.shape == (20000,) and ps.min() > 0 and ps.max() < 1
    assert abs(ns["ate_ipw"](df, ps) - 1.03) < 0.06, f"IPW: {ns['ate_ipw'](df, ps):.3f}"
    assert abs(ns["att_emparejamiento"](df, ps) - 1.02) < 0.08


def test_balance(ns):
    """SMD de x1 y x2: 0,69 y −0,52 antes; ≈ 0 tras la ponderación"""
    df = ns["simular_observacional"]()
    ps = ns["propension"](df)
    w = df["t"] / ps + (1 - df["t"]) / (1 - ps)
    assert abs(ns["smd"](df, "x1") - 0.688) < 0.01 and abs(ns["smd"](df, "x2") + 0.521) < 0.01
    assert abs(ns["smd"](df, "x1", w)) < 0.02 and abs(ns["smd"](df, "x2", w)) < 0.02


def test_propension_recupera_los_coeficientes(ns):
    """La logística debe aproximar 0,8·x1 − 0,6·x2: con un solo covariable el resultado cambia"""
    df = ns["simular_observacional"](n=50000, seed=3)
    completo = ns["propension"](df)
    parcial = ns["propension"](df, covariables=("x1",))
    assert np.corrcoef(completo, 1 / (1 + np.exp(-(0.8 * df["x1"] - 0.6 * df["x2"]))))[0, 1] > 0.999
    assert np.abs(completo - parcial).max() > 0.05


def test_hidden_sin_confusion_y_robustez(ns):
    """Sin confusión la comparación ingenua ya es correcta; el IPW no cambia el resultado (test oculto)"""
    rng = np.random.default_rng(5)
    import pandas as pd

    n = 30000
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    t = (rng.random(n) < 0.5).astype(int)
    y = 1.0 * t + 2 * x1 - 1.5 * x2 + rng.normal(size=n)
    df = pd.DataFrame({"x1": x1, "x2": x2, "t": t, "y": y})
    ps = ns["propension"](df)
    assert abs(ns["diferencia_ingenua"](df) - 1.0) < 0.1
    assert abs(ns["ate_ipw"](df, ps) - 1.0) < 0.1
    assert abs(ps.mean() - 0.5) < 0.01
    pesos_unitarios = np.ones(n)
    assert abs(ns["smd"](df, "x1", pesos_unitarios) - ns["smd"](df, "x1")) < 1e-9
