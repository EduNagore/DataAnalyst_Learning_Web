def test_normalizar(ns):
    """Minúsculas, sin tildes, sin palabras vacías y con raíz sencilla (plurales)"""
    n = ns["normalizar"]
    assert n("¿Cuántos pedidos no cancelados hubo por canal en 2025?") == {"2025", "canal", "cancelado", "no", "pedido"}
    assert n("Ingresos por categorías y márgenes de los productos") == {"categoria", "ingreso", "margen", "producto"}
    assert n("los de la") == set() and n("mes") == {"mes"} and n("ventas") == {"venta"}


def test_documento(ns):
    """El documento de una columna reúne tabla, nombre (partido por «_») y descripción"""
    d = ns["documento"]("orders", "order_date", ns["DESCRIPCIONES"])
    assert d == {"ano", "compro", "cuando", "date", "dia", "fecha", "mes", "order", "pedido"}
    assert ns["documento"]("orders", "order_date", None) == {"order", "date"}
    assert ns["documento"]("orders", "status", {}) == {"order", "statu"}, "La raíz sencilla recorta «status» a «statu»."


def test_enlazar(ns):
    """Devuelve las k columnas con más tokens en común; empates por orden del esquema; nunca puntuación 0"""
    e, d = ns["ESQUEMA"], ns["DESCRIPCIONES"]
    assert ns["enlazar"]("Motivos de devolución más frecuentes", e, d, 6) == ["returns.reason", "returns.return_date"]
    assert ns["enlazar"]("Ingresos por categoría de producto", e, d, 3) == ["products.category_id", "categories.name", "order_items.product_id"]
    assert ns["enlazar"]("xyz qwerty", e, d, 5) == []
    assert ns["enlazar"]("MRR de las suscripciones activas por plan", e, d, 2) == ["subscriptions.plan", "subscriptions.mrr_eur"]


def test_recall_con_y_sin_descripciones(ns):
    """Solo con los nombres (en inglés) el recall@6 es 0,27; con descripciones en lenguaje de negocio, 0,86"""
    o, e, d = ns["PREGUNTAS_ORO"], ns["ESQUEMA"], ns["DESCRIPCIONES"]
    assert abs(ns["recall_en_k"](o, e, None, 6) - 0.2708) < 0.001
    assert abs(ns["recall_en_k"](o, e, d, 6) - 0.8646) < 0.001
    assert abs(ns["recall_en_k"](o, e, d, 8) - 0.9062) < 0.001
    assert abs(ns["recall_en_k"](o, e, d, 1) - 0.375) < 0.001
    assert ns["recall_en_k"](o, e, d, 4) <= ns["recall_en_k"](o, e, d, 8)


def test_hidden_esquema_pequeno(ns):
    """Esquema de juguete con empates y una columna que solo aparece por su descripción (test oculto)"""
    esquema = {"ventas": ["id", "importe", "fecha"], "clientes": ["id", "nombre"]}
    desc = {"ventas.importe": "dinero facturado", "clientes.nombre": "razón social"}
    assert ns["enlazar"]("dinero de las ventas", esquema, desc, 5) == ["ventas.importe", "ventas.id", "ventas.fecha"]
    assert ns["enlazar"]("dinero de las ventas", esquema, None, 5) == ["ventas.id", "ventas.importe", "ventas.fecha"]
    oro = [("dinero facturado", {"ventas.importe"}), ("razón social del cliente", {"clientes.nombre", "clientes.id"})]
    assert abs(ns["recall_en_k"](oro, esquema, desc, 1) - 0.75) < 1e-9
    assert abs(ns["recall_en_k"](oro, esquema, desc, 3) - 0.75) < 1e-9, "«cliente» no comparte raíz con «clientes»: clientes.id nunca se enlaza."
