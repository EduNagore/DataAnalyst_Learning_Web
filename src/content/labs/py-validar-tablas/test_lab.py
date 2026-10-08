import pandas as pd
from datakit.data import load_raw, load_table

REGLAS = [
    "order_id_unico", "customer_id_no_nulo", "status_valido", "descuento_en_rango",
    "cliente_existe", "envio_numerico", "tienda_con_store_id",
]


def test_devuelve_las_siete_reglas(ns):
    """El informe contiene exactamente las siete reglas, con enteros"""
    r = ns["validar_pedidos"](ns["crudo"], ns["clientes"])
    assert list(r.keys()) == REGLAS, f"Reglas devueltas: {list(r.keys())}"
    assert all(isinstance(v, int) for v in r.values()), "Los contadores deben ser enteros de Python."


def test_informe_del_export_crudo(ns):
    """Informe del export crudo: 320 duplicadas, 143 clientes inexistentes, 8.160 importes de texto, 24 tiendas"""
    r = ns["validar_pedidos"](load_raw("orders"), load_table("customers"))
    esperado = {
        "order_id_unico": 320, "customer_id_no_nulo": 0, "status_valido": 0, "descuento_en_rango": 0,
        "cliente_existe": 143, "envio_numerico": 8160, "tienda_con_store_id": 24,
    }
    assert r == esperado, f"Informe: {r}"


def test_informe_de_la_tabla_limpia(ns):
    """Tras limpiar, solo quedan 140 clientes inexistentes y 24 tiendas sin id"""
    r = ns["validar_pedidos"](ns["limpio"], ns["clientes"])
    assert r["order_id_unico"] == 0 and r["envio_numerico"] == 0, f"Informe: {r}"
    assert r["cliente_existe"] == 140 and r["tienda_con_store_id"] == 24, f"Informe: {r}"


def test_exigir_lanza_con_fallos_no_tolerados(ns):
    """exigir lanza ValueError si hay fallos no tolerados y nombra las reglas"""
    informe = ns["validar_pedidos"](ns["limpio"], ns["clientes"])
    try:
        ns["exigir"](informe)
    except ValueError as e:
        assert "cliente_existe" in str(e), "El mensaje debe nombrar las reglas que fallan."
    else:
        raise AssertionError("exigir debería lanzar ValueError cuando hay fallos.")


def test_exigir_acepta_toleradas(ns):
    """exigir no lanza si todos los fallos están tolerados"""
    informe = ns["validar_pedidos"](ns["limpio"], ns["clientes"])
    ns["exigir"](informe, toleradas=frozenset({"cliente_existe", "tienda_con_store_id"}))


def test_hidden_tabla_pequena(ns):
    """Tabla pequeña con un fallo de cada tipo (test oculto)"""
    o = pd.DataFrame(
        {
            "order_id": ["a", "a", "b", "c", "d"],
            "customer_id": ["c1", "c1", None, "zz", "c2"],
            "status": ["completado", "completado", "raro", "cancelado", "completado"],
            "discount_pct": [0.1, 0.1, 0.9, 0.0, 0.2],
            "shipping_cost": ["4,95", "4,95", "2.95", "x", "0.0"],
            "channel": ["online", "online", "store", "store", "online"],
            "store_id": [None, None, None, "s1", None],
        }
    )
    clientes = pd.DataFrame({"customer_id": ["c1", "c2"]})
    r = ns["validar_pedidos"](o, clientes)
    assert r["order_id_unico"] == 2
    assert r["customer_id_no_nulo"] == 1
    assert r["status_valido"] == 1
    assert r["descuento_en_rango"] == 1
    assert r["cliente_existe"] == 2, "Un nulo tampoco existe en clientes: debe contar como incumplimiento."
    assert r["envio_numerico"] == 3, "'4,95' (x2) y 'x' no son números; '2.95' y '0.0' sí."
    assert r["tienda_con_store_id"] == 1
