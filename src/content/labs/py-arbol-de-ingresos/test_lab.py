import math

from datakit.data import load_table


def test_arbol_2025(ns):
    """El árbol de 2025 tiene 39.190 clientes activos y 161.706 pedidos"""
    r = ns["arbol_ingresos"](load_table("orders"), load_table("order_items"), 2025)
    assert set(r) == {"clientes_activos", "pedidos", "pedidos_por_cliente", "ticket_medio", "ingresos"}, f"Claves: {sorted(r)}"
    assert r["clientes_activos"] == 39190 and r["pedidos"] == 161706, f"Árbol: {r}"
    assert abs(r["pedidos_por_cliente"] - 4.126) < 0.0006 and abs(r["ticket_medio"] - 305.87) < 0.011, f"Árbol: {r}"
    assert abs(r["ingresos"] - 49460757.0) < 1.0, f"Ingresos: {r['ingresos']}"


def test_es_una_identidad(ns):
    """clientes × pedidos por cliente × ticket reproduce los ingresos (el árbol es MECE)"""
    r = ns["arbol_ingresos"](load_table("orders"), load_table("order_items"), 2024)
    producto = r["clientes_activos"] * r["pedidos_por_cliente"] * r["ticket_medio"]
    assert abs(producto / r["ingresos"] - 1) < 0.001, f"El producto de los factores ({producto:.0f}) no reproduce los ingresos."


def test_contribuciones(ns):
    """Las contribuciones de 2024 a 2025 son ≈ 75 % clientes, 24 % frecuencia y 1 % ticket, y suman 1"""
    o, i = load_table("orders"), load_table("order_items")
    c = ns["contribuciones"](ns["arbol_ingresos"](o, i, 2024), ns["arbol_ingresos"](o, i, 2025))
    assert abs(sum(c.values()) - 1) < 0.004, f"Las contribuciones deben sumar 1: {c}"
    assert abs(c["clientes_activos"] - 0.753) < 0.004 and abs(c["pedidos_por_cliente"] - 0.236) < 0.004, f"Contribuciones: {c}"
    assert abs(c["ticket_medio"] - 0.010) < 0.004, f"Contribuciones: {c}"


def test_hidden_arboles_artificiales(ns):
    """Con dos árboles inventados, el reparto logarítmico es exacto (test oculto)"""
    a = {"clientes_activos": 100, "pedidos_por_cliente": 2.0, "ticket_medio": 50.0, "ingresos": 10000.0}
    b = {"clientes_activos": 200, "pedidos_por_cliente": 2.0, "ticket_medio": 50.0, "ingresos": 20000.0}
    c = ns["contribuciones"](a, b)
    assert c["clientes_activos"] == 1.0 and c["pedidos_por_cliente"] == 0.0 and c["ticket_medio"] == 0.0, f"Contribuciones: {c}"
    b2 = {"clientes_activos": 100, "pedidos_por_cliente": 4.0, "ticket_medio": 100.0, "ingresos": 40000.0}
    c2 = ns["contribuciones"](a, b2)
    assert abs(c2["pedidos_por_cliente"] - 0.5) < 0.002 and abs(c2["ticket_medio"] - 0.5) < 0.002, f"Contribuciones: {c2}"
    assert math.isclose(sum(c2.values()), 1.0, abs_tol=0.003)
