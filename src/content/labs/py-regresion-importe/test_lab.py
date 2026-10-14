import numpy as np
import pandas as pd
from datakit.data import load_table


def _d(ns):
    return ns["datos_pedidos"](load_table("orders"), load_table("order_items"))


def test_datos(ns):
    """353.542 pedidos completados con las columnas del modelo"""
    d = _d(ns)
    assert len(d) == 353542, f"Filas: {len(d)}"
    assert {"discount_pct", "lineas", "unidades", "ln_importe", "ln_lineas"} <= set(d.columns)
    assert abs(np.exp(d["ln_importe"]).mean() - 301.7) < 1.0


def test_modelos_a_y_b(ns):
    """A: R² 0,356, líneas 0,512 y descuento −1,088; B: R² 0,398 con ln(líneas) 1,363"""
    d = _d(ns)
    a = ns["ols"](d, "ln_importe", ["lineas", "discount_pct"])
    assert abs(a["r2"] - 0.356) < 0.002
    t = a["tabla"]
    assert abs(t.loc["lineas", "coef"] - 0.5122) < 0.002 and abs(t.loc["discount_pct", "coef"] + 1.0881) < 0.01
    assert abs(t.loc["discount_pct", "se"] - 0.0173) < 0.002 and t.loc["lineas", "p"] < 1e-10
    b = ns["ols"](d, "ln_importe", ["ln_lineas", "discount_pct"])
    assert abs(b["r2"] - 0.398) < 0.002 and abs(b["tabla"].loc["ln_lineas", "coef"] - 1.3629) < 0.005
    ic = b["tabla"].loc["discount_pct"]
    assert ic["ic_inf"] < -1.09 < ic["ic_sup"]


def test_efecto_y_vif(ns):
    """−10 puntos de descuento restan un 10,3 %; líneas y unidades tienen VIF 3,76"""
    d = _d(ns)
    b = ns["ols"](d, "ln_importe", ["ln_lineas", "discount_pct"])
    assert abs(ns["efecto_pct"](b["tabla"].loc["discount_pct", "coef"], 0.1) + 10.34) < 0.2
    v = ns["vif"](d, ["lineas", "unidades", "discount_pct"])
    assert abs(v["lineas"] - 3.76) < 0.1 and abs(v["unidades"] - 3.76) < 0.1 and abs(v["discount_pct"] - 1.0) < 0.05


def test_hidden_datos_sinteticos(ns):
    """Coeficientes conocidos, R² y VIF con variables idénticas (test oculto)"""
    rng = np.random.default_rng(0)
    n = 5000
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    y = 2 + 3 * x1 - 1 * x2 + rng.normal(0, 0.5, n)
    df = pd.DataFrame({"y": y, "x1": x1, "x2": x2, "x3": x1 + rng.normal(0, 0.01, n)})
    r = ns["ols"](df, "y", ["x1", "x2"])
    t = r["tabla"]
    assert list(t.index) == ["const", "x1", "x2"]
    assert abs(t.loc["x1", "coef"] - 3) < 0.05 and abs(t.loc["x2", "coef"] + 1) < 0.05 and abs(t.loc["const", "coef"] - 2) < 0.05
    assert 0.97 < r["r2"] < 0.99
    assert ns["vif"](df, ["x1", "x2"])["x1"] < 1.05
    assert ns["vif"](df, ["x1", "x3"])["x1"] > 1000
    assert abs(ns["efecto_pct"](np.log(2)) - 100) < 1e-9 and abs(ns["efecto_pct"](0.0)) < 1e-12
