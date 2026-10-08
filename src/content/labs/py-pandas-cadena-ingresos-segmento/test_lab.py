from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _esperado(anio, variant=False):
    orders = load_table("orders", variant=variant)
    items = load_table("order_items", variant=variant)
    customers = load_table("customers", variant=variant)
    por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum().rename("ingresos")
    ped = orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == anio)]
    ped = ped.join(por_pedido, on="order_id").merge(customers[["customer_id", "segment"]], on="customer_id")
    ped["ingresos"] = ped["ingresos"].fillna(0.0)
    out = ped.groupby("segment", as_index=False).agg(pedidos=("order_id", "nunique"), ingresos=("ingresos", "sum"))
    out["ticket_medio"] = (out["ingresos"] / out["pedidos"]).round(2)
    return out


def test_columnas(ns):
    """Devuelve las columnas segment, pedidos, ingresos y ticket_medio"""
    r = ns["ingresos_por_segmento"](
        load_table("orders"), load_table("order_items"), load_table("customers"), 2025
    )
    assert_columns(r, ["segment", "pedidos", "ingresos", "ticket_medio"])


def test_cifras_2025(ns):
    """Las cifras de 2025 coinciden con la consulta SQL equivalente"""
    r = ns["ingresos_por_segmento"](
        load_table("orders"), load_table("order_items"), load_table("customers"), 2025
    )
    assert_frame_equivalent(r, _esperado(2025), sort_by=["segment"], tol=0.01)


def test_no_modifica_los_argumentos(ns):
    """No modifica los DataFrames de entrada"""
    orders = load_table("orders").head(5000)
    items = load_table("order_items")
    items = items[items["order_id"].isin(orders["order_id"])]
    customers = load_table("customers")
    cols = (list(orders.columns), list(items.columns), list(customers.columns))
    ns["ingresos_por_segmento"](orders, items, customers, 2025)
    assert (list(orders.columns), list(items.columns), list(customers.columns)) == cols, (
        "Has añadido columnas a un DataFrame de entrada. Usa `assign` y devuelve un resultado nuevo."
    )


def test_hidden_otro_anio_y_otros_datos(ns):
    """Funciona con otro año y con otro conjunto de datos (test oculto)"""
    r = ns["ingresos_por_segmento"](
        load_table("orders", variant=True),
        load_table("order_items", variant=True),
        load_table("customers", variant=True),
        2024,
    )
    assert_frame_equivalent(r, _esperado(2024, variant=True), sort_by=["segment"], tol=0.01)
