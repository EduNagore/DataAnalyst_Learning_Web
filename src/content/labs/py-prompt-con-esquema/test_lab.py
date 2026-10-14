import pandas as pd


def _p(ns, con_extras=True):
    if con_extras:
        return ns["construir_prompt"](ns["pregunta"], ns["esquemas"], ns["definiciones"], ns["ejemplos"])
    return ns["construir_prompt"](ns["pregunta"], ns["esquemas"])


def test_tipos_sql(ns):
    """Mapea los tipos de pandas a tipos SQL"""
    t = ns["tipo_sql"]
    assert t(pd.Series([True])) == "BOOLEAN" and t(pd.Series([1])) == "BIGINT" and t(pd.Series([1.5])) == "DOUBLE"
    assert t(pd.Series(pd.to_datetime(["2025-01-01"]))) == "TIMESTAMP" and t(pd.Series(["a"])) == "VARCHAR"


def test_estructura_del_prompt(ns):
    """Instrucción, esquema, definiciones, ejemplos, reglas y pregunta, en ese orden y sin filas de datos"""
    p = _p(ns)
    orden = ["DuckDB", "## Esquema", "## Definiciones de negocio", "## Ejemplos", "## Reglas", "## Pregunta"]
    posiciones = [p.index(x) for x in orden]
    assert posiciones == sorted(posiciones)
    assert "orders(order_id VARCHAR, customer_id VARCHAR, order_date TIMESTAMP, channel VARCHAR" in p
    assert "order_items(order_item_id VARCHAR, order_id VARCHAR, product_id VARCHAR, quantity BIGINT, unit_price DOUBLE)" in p
    assert "- ingresos_netos: SUM(" in p and "Pregunta: ¿Cuántos pedidos no cancelados" in p and "SQL: SELECT COUNT(*)" in p
    assert "NO_PUEDO_RESPONDER" in p and p.rstrip().endswith(ns["pregunta"])
    assert "order-0000000" not in p and "cust-" not in p


def test_secciones_opcionales_y_tamano(ns):
    """Sin definiciones ni ejemplos desaparecen sus secciones y el prompt pesa menos"""
    sin = _p(ns, False)
    assert "## Definiciones de negocio" not in sin and "## Ejemplos" not in sin
    assert "## Esquema" in sin and "## Reglas" in sin
    from datakit.llm import MockLLM

    assert MockLLM.count_tokens(sin) < MockLLM.count_tokens(_p(ns)) < 400


def test_auditoria_y_efecto_en_la_respuesta(ns):
    """El prompt bien construido pasa la auditoría y hace que el asistente simulado use la definición de negocio"""
    p, sin = _p(ns), _p(ns, False)
    assert ns["auditar_prompt"](p, ns["esquemas"], 2000) == []
    llm = ns["asistente_simulado"]()
    assert llm.complete(p) == ns["SQL_CORRECTO"] and ns["asistente_simulado"]().complete(sin) == ns["SQL_INGENUO"]


def test_hidden_auditoria_de_prompts_malos(ns):
    """Esquema incompleto, datos personales, sin regla de salida y presupuesto excedido (test oculto)"""
    malo = "Consulta orders(order_id VARCHAR). Fila de ejemplo: cust-012345, ana@correo.es, pedido 7."
    problemas = ns["auditar_prompt"](malo, ns["esquemas"], 10)
    assert problemas == [
        "sin_esquema:order_items",
        "sin_esquema:returns",
        "datos_personales",
        "sin_regla_de_salida",
        "excede_presupuesto",
    ]
    assert ns["auditar_prompt"]("orders(a) order_items(b) returns(c) NO_PUEDO_RESPONDER", ns["esquemas"], 100) == []
    solo_correo = "orders( order_items( returns( NO_PUEDO_RESPONDER pepe@ejemplo.com"
    assert ns["auditar_prompt"](solo_correo, ns["esquemas"], 100) == ["datos_personales"]
