import numpy as np
from datakit.data import load_table


def _muestra():
    orders = load_table("orders")
    items = load_table("order_items")
    imp = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
    orders["importe"] = orders["order_id"].map(imp).fillna(0.0)
    return orders.loc[orders["status"] == "completado", "importe"].sample(200, random_state=7).to_numpy()


def test_error_estandar_y_ic_t(ns):
    """Muestra de 200 pedidos: media 288,24 €, SE 22,77 € e IC t 95 % [243,3; 333,2]"""
    x = _muestra()
    assert abs(ns["error_estandar"](x) - 22.77) < 0.02, "El error estándar usa s muestral (ddof=1) dividida por √n."
    lo, hi = ns["ic_media_t"](x)
    assert abs(lo - 243.34) < 0.1 and abs(hi - 333.15) < 0.1, f"IC t: ({lo:.2f}, {hi:.2f})"
    assert lo < 301.70 < hi, "El intervalo debería contener la media poblacional (301,70 €)."


def test_bootstrap_media_y_mediana(ns):
    """Bootstrap de la media ≈ [245; 334] y de la mediana ≈ [141; 219]"""
    x = _muestra()
    lo, hi = ns["ic_bootstrap"](x)
    assert abs(lo - 245.1) < 6 and abs(hi - 334.3) < 6, f"Bootstrap media: ({lo:.1f}, {hi:.1f})"
    lo, hi = ns["ic_bootstrap"](x, np.median)
    assert abs(lo - 140.7) < 12 and abs(hi - 218.6) < 12, f"Bootstrap mediana: ({lo:.1f}, {hi:.1f})"


def test_wilson(ns):
    """22 cancelados de 500: Wilson [2,92 %; 6,57 %]"""
    lo, hi = ns["ic_wilson"](22, 500)
    assert abs(lo - 0.02923) < 0.0005 and abs(hi - 0.06572) < 0.0005, f"Wilson: ({lo:.5f}, {hi:.5f})"


def test_hidden_propiedades(ns):
    """Reproducibilidad, nivel, extremos y estadísticos arbitrarios (test oculto)"""
    x = np.array([10.0, 12.0, 9.0, 15.0, 11.0, 30.0, 8.0, 13.0, 12.5, 9.5])
    a = ns["ic_bootstrap"](x, seed=3)
    assert a == ns["ic_bootstrap"](x, seed=3), "Con la misma semilla el resultado debe repetirse."
    assert a != ns["ic_bootstrap"](x, seed=4), "Otra semilla debe dar otras remuestras."
    lo90, hi90 = ns["ic_bootstrap"](x, nivel=0.90, seed=3)
    lo99, hi99 = ns["ic_bootstrap"](x, nivel=0.99, seed=3)
    assert lo99 <= lo90 < hi90 <= hi99, "Un nivel mayor produce un intervalo más ancho."
    lo, hi = ns["ic_bootstrap"](x, np.std, seed=1)
    assert 0 < lo < hi, "Debe aceptar cualquier estadístico con `axis`."
    lo_t, hi_t = ns["ic_media_t"](x, nivel=0.99)
    lo_t95, hi_t95 = ns["ic_media_t"](x)
    assert lo_t < lo_t95 and hi_t > hi_t95
    lo0, hi0 = ns["ic_wilson"](0, 20)
    assert lo0 == 0.0 and abs(hi0 - 0.1611) < 0.001, f"k=0 → ({lo0}, {hi0})"
    lo1, hi1 = ns["ic_wilson"](20, 20)
    assert hi1 == 1.0 and abs(lo1 - 0.8389) < 0.001
