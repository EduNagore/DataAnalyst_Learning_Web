import pandas as pd
from datakit.data import load_raw, load_table
from datakit.testing import assert_columns, assert_frame_equivalent

COLUMNAS = [
    "order_id", "customer_id", "order_date", "channel", "device", "discount_pct",
    "shipping_cost", "status", "store_id", "cliente_valido", "tienda_sin_id",
]


def _limpio(ns):
    return ns["limpiar_pedidos"](load_raw("orders"), load_table("customers"))


def test_columnas_y_filas(ns):
    """Devuelve las columnas pedidas y una fila por pedido (8.000)"""
    r = _limpio(ns)
    assert_columns(r, COLUMNAS)
    assert len(r) == 8000, f"Esperaba 8.000 pedidos únicos y hay {len(r)} filas."
    assert r["order_id"].is_unique, "Quedan order_id repetidos."


def test_tipos(ns):
    """order_date es fecha y shipping_cost es numérico"""
    r = _limpio(ns)
    assert pd.api.types.is_datetime64_any_dtype(r["order_date"]), "order_date debe ser de tipo fecha."
    assert pd.api.types.is_float_dtype(r["shipping_cost"]), "shipping_cost debe ser numérico (float)."


def test_cifra_de_control(ns):
    """El envío total coincide con el del almacén (17.626,10 €)"""
    r = _limpio(ns)
    total = round(float(r["shipping_cost"].sum()), 2)
    assert abs(total - 17626.10) < 0.01, (
        f"El envío total es {total}; el almacén dice 17626.10. Revisa duplicados y decimales."
    )


def test_banderas(ns):
    """Las banderas marcan 140 pedidos con cliente inexistente y 24 de tienda sin store_id"""
    r = _limpio(ns)
    assert int((~r["cliente_valido"]).sum()) == 140, "cliente_valido debería ser False en 140 pedidos."
    assert int(r["tienda_sin_id"].sum()) == 24, "tienda_sin_id debería ser True en 24 pedidos."
    assert len(r) == 8000, "No elimines las filas con problemas: márcalas."


def test_coincide_con_el_almacen(ns):
    """Fechas, importes y estados coinciden con la tabla de pedidos limpia"""
    r = _limpio(ns)
    ok = r[r["cliente_valido"]]
    truth = load_table("orders")
    cols = ["order_id", "order_date", "channel", "device", "discount_pct", "shipping_cost", "status"]
    esperado = truth[truth["order_id"].isin(ok["order_id"])]
    assert_frame_equivalent(ok[cols], esperado[cols], sort_by=["order_id"])
    # Hay 8 pedidos asignados al cliente válido cust-000000 por error de origen: solo se ven al
    # contrastar con el almacén, no con un perfil del propio fichero.
    union = ok.merge(esperado[["order_id", "customer_id"]], on="order_id", suffixes=("", "_almacen"))
    distintos = union[union["customer_id"] != union["customer_id_almacen"]]
    assert len(distintos) <= 8, f"Hay {len(distintos)} pedidos con un customer_id distinto al del almacén."


def test_no_modifica_la_entrada(ns):
    """No modifica el DataFrame de entrada"""
    raw = load_raw("orders")
    antes = raw.copy()
    ns["limpiar_pedidos"](raw, load_table("customers"))
    assert raw.equals(antes), "Has modificado `raw`. Trabaja con copias y devuelve un resultado nuevo."


def test_hidden_casos_limite(ns):
    """Casos límite: fecha ambigua, duplicado, device n/a y banderas (test oculto)"""
    raw = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o2", "o3"],
            "customer_id": ["c1", "c2", "c2", "zzz"],
            "order_date": ["03/04/2024", "5 de marzo de 2023", "5 de marzo de 2023", "2025-12-31"],
            "channel": ["online", "store", "store", "online"],
            "device": ["mobile", None, None, "desktop"],
            "discount_pct": [0.1, 0.0, 0.0, 0.2],
            "shipping_cost": ["4,95", "0,00", "0,00", "2,95"],
            "status": ["completado", "completado", "completado", "cancelado"],
            "store_id": [None, None, None, None],
        }
    )
    clientes = pd.DataFrame({"customer_id": ["c1", "c2"]})
    r = ns["limpiar_pedidos"](raw, clientes).set_index("order_id")
    assert list(r.index) == ["o1", "o2", "o3"], f"Pedidos devueltos: {list(r.index)}"
    assert r.loc["o1", "order_date"] == pd.Timestamp(2024, 4, 3), "03/04/2024 es el 3 de abril."
    assert abs(r.loc["o1", "shipping_cost"] - 4.95) < 1e-9
    assert r.loc["o2", "device"] == "n/a", "En tienda el dispositivo es 'n/a', no un nulo."
    assert bool(r.loc["o2", "tienda_sin_id"]) is True
    assert bool(r.loc["o3", "cliente_valido"]) is False
    assert bool(r.loc["o1", "cliente_valido"]) is True
