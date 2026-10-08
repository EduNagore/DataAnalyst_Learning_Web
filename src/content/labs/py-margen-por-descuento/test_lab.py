import pandas as pd
from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _tabla(ns):
    return ns["margen_por_descuento"](load_table("orders"), load_table("order_items"), load_table("products"))


def test_columnas(ns):
    """La tabla tiene las columnas pedidas y seis niveles de descuento"""
    t = _tabla(ns)
    assert_columns(t, ["discount_pct", "pedidos", "margen_pct", "margen_por_pedido"])
    assert len(t) == 6, f"Se esperaban 6 niveles de descuento y hay {len(t)}."


def test_cifras(ns):
    """El margen cae del 42,5 % (sin descuento) al 17,7 % (30 %) y de 142,1 € a 42,6 € por pedido"""
    esperado = pd.DataFrame(
        {
            "discount_pct": [0.0, 0.05, 0.10, 0.15, 0.20, 0.30],
            "pedidos": [123093, 48979, 74152, 29227, 58024, 43670],
            "margen_pct": [42.5, 39.5, 36.0, 32.4, 28.0, 17.7],
            "margen_por_pedido": [142.1, 125.5, 109.3, 92.3, 76.1, 42.6],
        }
    )
    assert_frame_equivalent(_tabla(ns), esperado, sort_by=["discount_pct"], tol=0.11)


def test_ratio(ns):
    """Un pedido con el máximo descuento conserva el 0,30 del margen de uno sin descuento"""
    r = ns["ratio_margen_goodhart"](_tabla(ns))
    assert abs(r - 0.30) < 0.011, f"Ratio: {r}"


def test_no_modifica_la_entrada(ns):
    """No modifica los DataFrames de entrada"""
    o, i, p = load_table("orders"), load_table("order_items"), load_table("products")
    cols = (list(o.columns), list(i.columns), list(p.columns))
    ns["margen_por_descuento"](o, i, p)
    assert (list(o.columns), list(i.columns), list(p.columns)) == cols, "Has añadido columnas a una tabla de entrada."


def test_hidden_tabla_pequena(ns):
    """Con una tabla mínima, el ratio es exacto (test oculto)"""
    t = pd.DataFrame(
        {"discount_pct": [0.0, 0.3], "pedidos": [10, 5], "margen_pct": [40.0, 10.0], "margen_por_pedido": [100.0, 25.0]}
    )
    assert ns["ratio_margen_goodhart"](t) == 0.25
