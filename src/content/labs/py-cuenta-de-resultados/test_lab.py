import pandas as pd
from datakit.data import load_table


def _lin(ns):
    return ns["lineas_pedido"](
        load_table("orders"), load_table("order_items"), load_table("products"), load_table("returns")
    )


def _pyg(ns, anio):
    return ns["pyg"](_lin(ns), load_table("orders"), load_table("marketing_spend"), anio)


def test_lineas(ns):
    """Solo pedidos no cancelados; las líneas devueltas se marcan con `devuelta`"""
    lin = _lin(ns)
    assert {"order_id", "fecha", "cantidad", "precio_lista", "precio_final", "coste_unitario", "devuelta"} <= set(lin.columns)
    assert len(lin) == 974190 and int(lin["devuelta"].sum()) == 68218


def test_cuenta_de_resultados_2025(ns):
    """2025: ventas netas 45,94 M€; margen bruto 35,7 %; contribución 14,73 M€ (32,1 %)"""
    p = _pyg(ns, 2025)
    assert abs(p["ventas_brutas"] / 1e6 - 49.461) < 0.001 and abs(p["devoluciones"] / 1e6 - 3.518) < 0.001
    assert abs(p["ventas_netas"] / 1e6 - 45.942) < 0.001 and abs(p["margen_bruto_pct"] - 35.71) < 0.01
    assert abs(p["contribucion"] / 1e6 - 14.727) < 0.001 and abs(p["contribucion_pct"] - 32.06) < 0.01
    assert abs(p["descuentos"] / p["ventas_lista"] - 0.0989) < 0.001, "Los descuentos suponen ≈ 9,9 % del precio de lista."


def test_comparacion_interanual(ns):
    """La contribución crece un 148,6 % porque el marketing solo sube un 7,1 %"""
    t = ns["comparar"](_pyg(ns, 2024), _pyg(ns, 2025))
    assert list(t.columns) == ["anterior", "actual", "variacion_pct"]
    assert abs(t.loc["ventas_netas", "variacion_pct"] - 119.92) < 0.05
    assert abs(t.loc["marketing", "variacion_pct"] - 7.13) < 0.05
    assert abs(t.loc["contribucion", "variacion_pct"] - 148.64) < 0.05
    assert abs(t.loc["margen_bruto_pct", "variacion_pct"] - 0.66) < 0.02, "Las partidas en % se comparan en puntos."


def test_hidden_caso_pequeno(ns):
    """Un pedido con devolución, descuento y envío calculado a mano (test oculto)"""
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "customer_id": ["c1", "c2"],
            "order_date": pd.to_datetime(["2025-03-01", "2025-04-01"]),
            "status": ["completado", "cancelado"],
            "shipping_cost": [5.0, 5.0],
        }
    )
    items = pd.DataFrame(
        {
            "order_item_id": ["i1", "i2", "i3"],
            "order_id": ["o1", "o1", "o2"],
            "product_id": ["p1", "p2", "p1"],
            "quantity": [2, 1, 1],
            "unit_price": [9.0, 20.0, 9.0],
        }
    )
    products = pd.DataFrame({"product_id": ["p1", "p2"], "price": [10.0, 25.0], "cost": [6.0, 12.0]})
    devol = pd.DataFrame({"return_id": ["r1"], "order_item_id": ["i2"]})
    gasto = pd.DataFrame({"date": pd.to_datetime(["2025-03-10", "2024-03-10"]), "channel": ["a", "a"], "spend_eur": [3.0, 100.0]})
    lin = ns["lineas_pedido"](orders, items, products, devol)
    assert len(lin) == 2 and int(lin["devuelta"].sum()) == 1
    p = ns["pyg"](lin, orders, gasto, 2025)
    assert p["ventas_lista"] == 45 and p["ventas_brutas"] == 38 and p["descuentos"] == 7
    assert p["devoluciones"] == 20 and p["ventas_netas"] == 18 and p["coste_producto"] == 12
    assert p["margen_bruto"] == 6 and p["envios"] == 5 and p["marketing"] == 3 and p["contribucion"] == -2
