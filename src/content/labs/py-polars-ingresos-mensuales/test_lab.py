import polars as pl
from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _lazy(name, variant=False):
    return pl.from_pandas(load_table(name, variant=variant)).lazy()


def _collect(r):
    assert r is not None, "La función no devuelve nada: añade el `return`."
    return r.collect() if hasattr(r, "collect") else r


def _esperado(anio, variant=False):
    orders = load_table("orders", variant=variant)
    items = load_table("order_items", variant=variant)
    m = items.merge(orders[["order_id", "order_date", "status"]], on="order_id")
    m = m[(m["status"] != "cancelado") & (m["order_date"].dt.year == anio)]
    m = m.assign(ingresos=m["quantity"] * m["unit_price"], mes=m["order_date"].dt.month)
    out = m.groupby("mes", as_index=False)["ingresos"].sum().sort_values("mes").reset_index(drop=True)
    out["crec_pct"] = (out["ingresos"].pct_change() * 100).round(1)
    return out


def test_columnas(ns):
    """Devuelve las columnas mes, ingresos y crec_pct"""
    r = _collect(ns["ingresos_mensuales"](_lazy("orders"), _lazy("order_items"), 2025))
    assert_columns(r.to_pandas(), ["mes", "ingresos", "crec_pct"])


def test_cifras_2025(ns):
    """Ingresos y crecimiento de 2025 correctos y ordenados por mes"""
    r = _collect(ns["ingresos_mensuales"](_lazy("orders"), _lazy("order_items"), 2025)).to_pandas()
    assert r["mes"].tolist() == sorted(r["mes"].tolist()), "El resultado debe estar ordenado por mes."
    assert_frame_equivalent(r, _esperado(2025), tol=0.06)


def test_primer_mes_es_null(ns):
    """El crecimiento del primer mes es null"""
    r = _collect(ns["ingresos_mensuales"](_lazy("orders"), _lazy("order_items"), 2025))
    assert r["crec_pct"][0] is None, "El primer mes no tiene mes anterior: crec_pct debe ser null."


def test_hidden_otro_anio_y_otros_datos(ns):
    """Funciona con otro año y con otro conjunto de datos (test oculto)"""
    r = _collect(
        ns["ingresos_mensuales"](_lazy("orders", True), _lazy("order_items", True), 2024)
    ).to_pandas()
    assert_frame_equivalent(r, _esperado(2024, variant=True), tol=0.06)
