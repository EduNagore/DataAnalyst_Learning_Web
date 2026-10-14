import pandas as pd


def test_un_hash_sin_clave_se_revierte(ns):
    """Con los identificadores de Lumen (cust-000000…) un SHA-256 sin clave se reidentifica al 100 %"""
    ids = ns["clientes"]["customer_id"].tolist()
    simples = [ns["hash_simple"](i) for i in ids[:3000]]
    assert ns["tasa_de_reidentificacion"](simples, ids) == 100.0
    assert ns["ataque_de_diccionario"](ns["hash_simple"](ids[1234]), ids) == ids[1234]
    assert ns["ataque_de_diccionario"]("0" * 64, ids[:100]) is None


def test_un_seudonimo_con_clave_resiste(ns):
    """Con HMAC y clave secreta, el mismo ataque no recupera ningún identificador, y el seudónimo es estable"""
    ids = ns["clientes"]["customer_id"].tolist()
    con_clave = [ns["seudonimo"](i, ns["CLAVE"]) for i in ids[:3000]]
    assert ns["tasa_de_reidentificacion"](con_clave, ids) == 0.0
    assert ns["seudonimo"]("cust-000001", ns["CLAVE"]) == ns["seudonimo"]("cust-000001", ns["CLAVE"])
    assert ns["seudonimo"]("cust-000001", ns["CLAVE"]) != ns["seudonimo"]("cust-000001", b"otra-clave")
    assert len(set(con_clave)) == 3000 and len(con_clave[0]) == 64


def test_seudonimizar_y_minimizar(ns):
    """La tabla seudonimizada no contiene el identificador original, conserva las filas y solo las columnas necesarias"""
    c = ns["clientes"]
    m = ns["minimizar"](c, ["customer_id", "segment", "region"])
    assert list(m.columns) == ["customer_id", "segment", "region"] and len(m) == len(c)
    t = ns["seudonimizar_tabla"](m, "customer_id", ns["CLAVE"])
    assert "customer_id" not in t.columns and "seudonimo" in t.columns and len(t) == 60000
    assert t["seudonimo"].is_unique
    assert list(t["segment"]) == list(c["segment"]), "El orden de las filas se conserva."


def test_hidden_tabla_pequena(ns):
    """Caso a mano: columnas, orden, seudónimos distintos con claves distintas (test oculto)"""
    df = pd.DataFrame({"id": ["a", "b", "a"], "x": [1, 2, 3], "nombre": ["Ana", "Beto", "Ana"]})
    m = ns["minimizar"](df, ["x", "id"])
    assert list(m.columns) == ["x", "id"] and "nombre" not in m.columns
    t1 = ns["seudonimizar_tabla"](df, "id", b"k1")
    t2 = ns["seudonimizar_tabla"](df, "id", b"k2")
    assert t1["seudonimo"].iloc[0] == t1["seudonimo"].iloc[2] != t1["seudonimo"].iloc[1]
    assert list(t1["seudonimo"]) != list(t2["seudonimo"])
    assert "id" not in t1.columns and list(t1["x"]) == [1, 2, 3]
    assert df.columns.tolist() == ["id", "x", "nombre"], "No debe modificar el DataFrame original."
