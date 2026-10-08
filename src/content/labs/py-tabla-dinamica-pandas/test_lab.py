import pandas as pd
from datakit.data import load_table


def _por_pedido():
    items = load_table("order_items")
    return (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()


def test_ingresos_por_pedido(ns):
    """Cada pedido lleva la suma de sus líneas y la tabla conserva todas las filas de orders"""
    orders = load_table("orders")
    r = ns["ingresos_por_pedido"](orders, load_table("order_items"))
    assert len(r) == len(orders) and "ingresos" in r.columns, "Debe conservar los pedidos y añadir `ingresos`."
    assert abs(r["ingresos"].sum() - _por_pedido().sum()) < 0.5, "La suma de ingresos no coincide con las líneas."
    assert "ingresos" not in orders.columns, "No modifiques la tabla de entrada."


def test_agrupar_por_canal(ns):
    """Ingresos por canal, de mayor a menor"""
    p = ns["ingresos_por_pedido"](load_table("orders"), load_table("order_items"))
    r = ns["agrupar_por"](p, "channel", "ingresos")
    assert list(r.columns) == ["channel", "ingresos"], f"Columnas: {list(r.columns)}"
    assert r["ingresos"].is_monotonic_decreasing and r.loc[0, "channel"] == "online"
    esperado = p.groupby("channel")["ingresos"].sum()
    for _, fila in r.iterrows():
        assert abs(fila["ingresos"] - esperado[fila["channel"]]) < 0.5


def test_pivotar_con_totales(ns):
    """Tabla canal × estado con fila y columna Total que cuadran"""
    p = ns["ingresos_por_pedido"](load_table("orders"), load_table("order_items"))
    t = ns["pivotar_por"](p, "channel", "status", "ingresos")
    assert {"online", "store", "Total"} <= set(t.index), f"Filas: {list(t.index)}"
    assert {"completado", "cancelado", "devuelto_parcial", "Total"} <= set(t.columns)
    assert abs(t.loc["Total", "Total"] - p["ingresos"].sum()) < 0.5
    online_ok = p.query("channel == 'online' and status == 'completado'")["ingresos"].sum()
    assert abs(t.loc["online", "completado"] - online_ok) < 0.5
    assert ns["diferencia_cuadre"](t, p, "ingresos") < 0.5


def test_hidden_sin_totales_y_conteo(ns):
    """Sin totales, con conteo y celdas vacías a 0 (test oculto)"""
    df = pd.DataFrame({"a": ["x", "x", "y"], "b": ["m", "n", "m"], "v": [1.0, 2.0, 4.0]})
    t = ns["pivotar_por"](df, "a", "b", "v", totales=False)
    assert "Total" not in t.index and "Total" not in t.columns
    assert t.loc["y", "n"] == 0, "Las celdas sin datos deben quedar a 0."
    c = ns["pivotar_por"](df, "a", "b", "v", funcion="count")
    assert c.loc["x", "Total"] == 2 and c.loc["Total", "Total"] == 3
    g = ns["agrupar_por"](df, "a", "v", "mean")
    assert list(g["a"]) == ["y", "x"] and list(g["v"]) == [4.0, 1.5]
    assert ns["diferencia_cuadre"](ns["pivotar_por"](df, "a", "b", "v"), df, "v") == 0
