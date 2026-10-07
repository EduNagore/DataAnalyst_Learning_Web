from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _esperado(orders):
    out = (
        orders.assign(anio=orders["order_date"].dt.year)
        .groupby(["anio", "channel"])
        .size()
        .reset_index(name="pedidos")
    )
    return out


def test_pedidos_por_canal_y_anio_tiene_las_columnas_correctas(ns):
    """pedidos_por_canal_y_anio devuelve las columnas anio, channel y pedidos"""
    result = ns["pedidos_por_canal_y_anio"](load_table("orders"))
    assert_columns(result, ["anio", "channel", "pedidos"])


def test_pedidos_por_canal_y_anio_cifras(ns):
    """Las cifras por año y canal coinciden con las esperadas"""
    orders = load_table("orders")
    result = ns["pedidos_por_canal_y_anio"](orders)
    assert_frame_equivalent(result, _esperado(orders), sort_by=["anio", "channel"])


def test_marcar_envio_gratis_anade_la_columna(ns):
    """marcar_envio_gratis añade envio_gratis (True cuando el envío cuesta 0)"""
    orders = load_table("orders").head(2000)
    result = ns["marcar_envio_gratis"](orders)
    assert_columns(result, ["envio_gratis"])
    esperado = (orders["shipping_cost"] == 0).tolist()
    assert result["envio_gratis"].tolist() == esperado, "La columna envio_gratis no coincide con shipping_cost == 0."


def test_marcar_envio_gratis_no_modifica_el_original(ns):
    """marcar_envio_gratis no modifica el DataFrame que recibe"""
    orders = load_table("orders").head(2000)
    columnas_antes = list(orders.columns)
    ns["marcar_envio_gratis"](orders)
    assert list(orders.columns) == columnas_antes, (
        "Tu función ha añadido una columna al DataFrame original. "
        "Devuelve una copia (por ejemplo con `assign`) en vez de modificar el argumento."
    )


def test_hidden_funciona_con_otros_datos(ns):
    """Funciona también con otro conjunto de datos (test oculto)"""
    orders = load_table("orders", variant=True)
    result = ns["pedidos_por_canal_y_anio"](orders)
    assert_frame_equivalent(result, _esperado(orders), sort_by=["anio", "channel"])
