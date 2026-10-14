def test_limpieza(ns):
    """Quita comentarios y un «;» final; los literales se vacían"""
    assert ns["limpiar_sql"]("SELECT 1 /* x; DROP */ -- y\n ;") == "SELECT 1"
    assert ns["limpiar_sql"]("  select 1  ") == "select 1"
    assert ns["sin_literales"]("a = 'x; DROP' AND b = 'it''s'") == "a = '' AND b = ''"


def test_consultas_legitimas(ns):
    """Las consultas de solo lectura sobre tablas permitidas pasan, también con CTE, JOIN, comentarios y literales «peligrosos»"""
    v, p = ns["validar"], ns["POLITICA"]
    buenas = [
        "SELECT segment, COUNT(*) FROM customers GROUP BY 1",
        "select * from customers where segment = 'vip'",
        "SeLeCt * FrOm ORDERS",
        "SELECT * FROM customers; ",
        "SELECT * FROM customers /* ; DROP TABLE x */",
        "SELECT 'delete me; drop table x' AS t",
        "WITH a AS (SELECT * FROM customers) SELECT * FROM a",
        "SELECT * FROM customers c JOIN orders o USING (customer_id)",
        "SELECT * FROM (SELECT * FROM customers) q",
    ]
    for q in buenas:
        assert v(q, p) == (True, "ok"), q


def test_ataques_rechazados(ns):
    """Sentencias apiladas, escritura, lectura de ficheros, comandos de administración y tablas fuera de la lista se rechazan con su motivo"""
    v, p = ns["validar"], ns["POLITICA"]
    casos = {
        "SELECT 1; DROP TABLE customers": "multiples_sentencias",
        "DELETE FROM customers": "no_es_select",
        "COPY customers TO 'x.csv'": "no_es_select",
        "ATTACH 'x.db'": "no_es_select",
        "WITH x AS (SELECT 1) DELETE FROM customers": "palabra_prohibida:delete",
        "SELECT * FROM read_csv('/etc/passwd')": "palabra_prohibida:read_csv",
        "SELECT * FROM secretos": "tabla_no_permitida:secretos",
        "SELECT * FROM main.customers": "tabla_no_permitida:main.customers",
        "SELECT * FROM cust/**/omers": "tabla_no_permitida:cust",
        "": "vacia",
        "-- solo un comentario": "vacia",
    }
    for q, motivo in casos.items():
        assert v(q, p) == (False, motivo), q


def test_ejecucion_con_limites(ns):
    """Se ejecuta con LIMIT: 4 filas para el recuento por segmento; 1.000 y truncado para toda la tabla de 60.000 clientes"""
    p = ns["POLITICA"]
    r = ns["ejecutar_seguro"]("SELECT segment, COUNT(*) AS n FROM customers GROUP BY 1", p)
    assert r["estado"] == "ok" and len(r["filas"]) == 4 and r["truncado"] is False
    r = ns["ejecutar_seguro"]("SELECT * FROM customers", p)
    assert r["estado"] == "ok" and len(r["filas"]) == 1000 and r["truncado"] is True
    r = ns["ejecutar_seguro"]("SELECT * FROM customers", {**p, "max_filas": 5})
    assert len(r["filas"]) == 5 and r["truncado"] is True
    r = ns["ejecutar_seguro"]("SELECT 1; DROP TABLE customers", p)
    assert r == {"estado": "rechazada", "motivo": "multiples_sentencias", "filas": None, "truncado": False}
    r = ns["ejecutar_seguro"]("SELECT columna_inexistente FROM customers", p)
    assert r["estado"] == "error" and r["filas"] is None and r["motivo"]


def test_hidden_auditoria(ns):
    """La auditoría guarda un hash del SQL, no el SQL ni los datos (test oculto)"""
    aud = []
    p = ns["POLITICA"]
    sql = "SELECT segment, COUNT(*) AS n FROM customers GROUP BY 1 -- comentario"
    e1 = ns["registrar"](aud, "ana", sql, ns["ejecutar_seguro"](sql, p))
    e2 = ns["registrar"](aud, "ana", "DROP TABLE customers", ns["ejecutar_seguro"]("DROP TABLE customers", p))
    assert aud == [e1, e2] and len(e1["sql_hash"]) == 12
    assert e1 == {"usuario": "ana", "sql_hash": e1["sql_hash"], "estado": "ok", "motivo": "ok", "n_filas": 4}
    assert e2["estado"] == "rechazada" and e2["n_filas"] == 0 and e2["motivo"] == "no_es_select"
    mismo = ns["registrar"]([], "luis", "SELECT segment, COUNT(*) AS n FROM customers GROUP BY 1", {"estado": "ok", "motivo": "ok", "filas": None})
    assert mismo["sql_hash"] == e1["sql_hash"], "El hash se calcula sobre la consulta limpia (sin comentarios)."
    assert "sql" not in e1 and "filas" not in e1
