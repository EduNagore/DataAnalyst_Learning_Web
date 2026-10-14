import pandas as pd
from datakit.data import load_table


def test_puntualidad(ns):
    """82,0 % a tiempo; 10,7 % con 5 días o más de retraso; sin diferencias relevantes entre transportistas"""
    sh = load_table("shipments")
    r = ns["retraso_dias"](sh)
    assert r.min() == -1 and r.max() == 10 and len(r) == 365198
    assert abs(ns["puntualidad"](sh) - 81.99) < 0.01 and abs(ns["retraso_grave"](sh) - 10.73) < 0.01
    por = ns["puntualidad"](sh, "carrier")
    assert set(por.index) == {"Correos", "CorreosExpress", "GLS", "MRW", "SEUR"}
    assert por.max() - por.min() < 0.5


def test_rotura_de_electronica(ns):
    """Marzo de 2026: stock medio de Electrónica 85 unidades (212 en febrero) y 19,6 % de registros sin stock"""
    r = ns["rotura_mensual"](load_table("inventory_snapshots"), load_table("products"), "cat-00")
    feb, mar, abr = (r.loc[pd.Period(m, "M")] for m in ("2026-02", "2026-03", "2026-04"))
    assert abs(mar["stock_medio"] - 85.1) < 0.2 and abs(feb["stock_medio"] - 212.0) < 0.3
    assert abs(mar["pct_sin_stock"] - 19.6) < 0.1 and feb["pct_sin_stock"] == 0 and abr["pct_sin_stock"] == 0
    resto = ns["rotura_mensual"](load_table("inventory_snapshots"), load_table("products"), "cat-01")
    assert resto["pct_sin_stock"].max() < 0.5, "Las demás categorías prácticamente no tienen roturas."


def test_rotacion(ns):
    """2025: coste de ventas 31,80 M€ entre un inventario medio de 88,0 M€ = 0,36 vueltas (≈ 1.010 días de cobertura)"""
    r = ns["rotacion_inventario"](
        load_table("inventory_snapshots"), load_table("products"), load_table("orders"), load_table("order_items"), 2025
    )
    assert abs(r["coste_ventas"] / 1e6 - 31.799) < 0.001 and abs(r["valor_medio"] / 1e6 - 88.011) < 0.001
    assert abs(r["rotacion"] - 0.3613) < 0.001 and abs(r["dias_cobertura"] - 1010.2) < 0.5


def test_hidden_casos_pequenos(ns):
    """Retrasos y rotación calculados a mano (test oculto)"""
    sh = pd.DataFrame(
        {
            "promised_date": pd.to_datetime(["2025-01-10", "2025-01-10", "2025-01-10", "2025-01-10"]),
            "actual_date": pd.to_datetime(["2025-01-09", "2025-01-10", "2025-01-13", "2025-01-16"]),
            "carrier": ["A", "A", "B", "B"],
        }
    )
    assert list(ns["retraso_dias"](sh)) == [-1, 0, 3, 6]
    assert abs(ns["puntualidad"](sh) - 50) < 1e-9 and abs(ns["retraso_grave"](sh) - 25) < 1e-9
    por = ns["puntualidad"](sh, "carrier")
    assert por["A"] == 100 and por["B"] == 0
    inv = pd.DataFrame(
        {
            "snapshot_date": pd.to_datetime(["2025-01-06", "2025-01-06", "2025-01-13", "2025-01-13"]),
            "product_id": ["p1", "p2", "p1", "p2"],
            "location_id": ["dc", "dc", "dc", "dc"],
            "stock_qty": [10, 20, 30, 0],
        }
    )
    prod = pd.DataFrame({"product_id": ["p1", "p2"], "cost": [2.0, 5.0]})
    ped = pd.DataFrame({"order_id": ["o1", "o2"], "order_date": pd.to_datetime(["2025-02-01", "2025-02-02"]), "status": ["completado", "cancelado"]})
    items = pd.DataFrame({"order_id": ["o1", "o2"], "product_id": ["p1", "p2"], "quantity": [10, 99]})
    r = ns["rotacion_inventario"](inv, prod, ped, items, 2025)
    assert abs(r["valor_medio"] - 90) < 1e-9, "Valor por fecha: 120 y 60; se suma por fecha y se promedian las fechas."
    assert r["coste_ventas"] == 20 and abs(r["rotacion"] - 20 / 90) < 1e-9 and abs(r["dias_cobertura"] - 1642.5) < 1e-6
