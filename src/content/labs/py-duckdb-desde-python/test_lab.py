import pandas as pd
from datakit.data import load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _esperado(desde, variant=False):
    customers = load_table("customers", variant=variant)
    orders = load_table("orders", variant=variant)
    d = pd.Timestamp(desde)
    activos = set(orders.loc[(orders["status"] != "cancelado") & (orders["order_date"] >= d), "customer_id"])
    base = customers[customers["signup_date"] < d].copy()
    base["inactivo"] = ~base["customer_id"].isin(activos)
    out = base.groupby("segment", as_index=False).agg(clientes=("customer_id", "count"), inactivos=("inactivo", "sum"))
    out["inactivos"] = out["inactivos"].astype(int)
    out["pct_inactivos"] = (100.0 * out["inactivos"] / out["clientes"]).round(1)
    return out


def _resultado(ns, desde, variant=False):
    r = ns["inactivos_por_segmento"](
        load_table("customers", variant=variant), load_table("orders", variant=variant), desde
    )
    assert isinstance(r, pd.DataFrame), "La función debe devolver un DataFrame de pandas (usa `.df()`)."
    return r


def test_columnas(ns):
    """Devuelve las columnas segment, clientes, inactivos y pct_inactivos"""
    assert_columns(_resultado(ns, "2026-01-01"), ["segment", "clientes", "inactivos", "pct_inactivos"])


def test_cifras(ns):
    """Las cifras coinciden con el cálculo independiente en pandas"""
    assert_frame_equivalent(_resultado(ns, "2026-01-01"), _esperado("2026-01-01"), sort_by=["segment"], tol=0.06)


def test_usa_el_parametro(ns):
    """El resultado cambia con la fecha (el parámetro se usa de verdad)"""
    a = _resultado(ns, "2026-01-01")
    b = _resultado(ns, "2025-06-01")
    assert a["clientes"].sum() != b["clientes"].sum(), "Con otra fecha deberían cambiar los clientes considerados."
    assert_frame_equivalent(b, _esperado("2025-06-01"), sort_by=["segment"], tol=0.06)


def test_hidden_otros_datos(ns):
    """Funciona con otro conjunto de datos (test oculto)"""
    assert_frame_equivalent(
        _resultado(ns, "2026-01-01", variant=True), _esperado("2026-01-01", variant=True), sort_by=["segment"], tol=0.06
    )
