import pandas as pd
from datakit.data import load_table
from datakit.testing import assert_columns


def _hechos(ns):
    return ns["construir_hechos"](load_table("order_items"), load_table("orders"))


def test_grano_y_columnas(ns):
    """El hecho tiene una fila por línea de pedido (1.014.555) con clave única y las columnas pedidas"""
    h = _hechos(ns)
    assert_columns(h, ["order_item_id", "order_id", "customer_id", "product_id", "fecha_id", "cantidad", "importe", "estado"])
    assert len(h) == 1014555, f"Se esperaban 1.014.555 líneas y hay {len(h)}: ¿has duplicado filas al unir?"
    assert h["order_item_id"].is_unique, "order_item_id debe ser único (el grano es la línea)."


def test_cifra_de_control(ns):
    """La suma del importe del hecho es 118,57 M€, igual que la de order_items"""
    h = _hechos(ns)
    items = load_table("order_items")
    esperado = float((items["quantity"] * items["unit_price"]).sum())
    assert abs(float(h["importe"].sum()) - esperado) < 1.0, "El total del hecho no coincide con el de order_items."
    assert abs(esperado / 1e6 - 118.57) < 0.01


def test_fecha_id_y_dimension_de_fechas(ns):
    """fecha_id es AAAAMMDD y la dimensión de fechas no tiene huecos"""
    h = _hechos(ns)
    assert h["fecha_id"].between(20230101, 20260630).all(), "fecha_id debe estar entre 20230101 y 20260630."
    o = load_table("orders")
    d = ns["dim_fecha"](o["order_date"].min(), o["order_date"].max())
    assert_columns(d, ["fecha_id", "fecha", "anio", "mes", "trimestre", "dia_semana"])
    assert d["fecha_id"].is_unique
    pasos = d["fecha"].sort_values().diff().dropna().dt.days
    assert (pasos == 1).all(), "La dimensión de fechas debe tener todos los días consecutivos, sin huecos."
    assert len(d) == (o["order_date"].max() - o["order_date"].min()).days + 1


def test_integridad_referencial(ns):
    """Ninguna fila del hecho queda huérfana"""
    h = _hechos(ns)
    o = load_table("orders")
    d = ns["dim_fecha"](o["order_date"].min(), o["order_date"].max())
    r = ns["comprobar_integridad"](h, load_table("customers"), load_table("products"), d)
    assert r == {"clientes_huerfanos": 0, "productos_huerfanos": 0, "fechas_huerfanas": 0}, f"Integridad: {r}"


def test_hidden_detecta_huerfanos(ns):
    """Con tablas pequeñas, detecta claves que no existen y calcula bien fecha_id (test oculto)"""
    items = pd.DataFrame(
        {"order_item_id": ["i1", "i2"], "order_id": ["o1", "o1"], "product_id": ["p1", "pX"], "quantity": [2, 1], "unit_price": [10.0, 5.0]}
    )
    orders = pd.DataFrame(
        {"order_id": ["o1"], "customer_id": ["c9"], "order_date": [pd.Timestamp("2025-03-07")], "status": ["completado"]}
    )
    h = ns["construir_hechos"](items, orders)
    assert list(h["fecha_id"]) == [20250307, 20250307] and list(h["importe"]) == [20.0, 5.0]
    d = ns["dim_fecha"]("2025-03-01", "2025-03-05")
    assert len(d) == 5 and d["dia_semana"].iloc[0] == 5, "El 1 de marzo de 2025 fue sábado (5)."
    r = ns["comprobar_integridad"](h, pd.DataFrame({"customer_id": ["c1"]}), pd.DataFrame({"product_id": ["p1"]}), d)
    assert r == {"clientes_huerfanos": 2, "productos_huerfanos": 1, "fechas_huerfanas": 2}, f"Integridad: {r}"
