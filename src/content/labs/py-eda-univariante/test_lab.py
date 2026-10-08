import numpy as np
import pandas as pd
from datakit.data import load_table


def _datos(variant=False):
    orders = load_table("orders", variant=variant)
    items = load_table("order_items", variant=variant)
    ok = orders[orders["status"] != "cancelado"]
    por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
    importes = por_pedido.reindex(ok["order_id"]).reset_index(drop=True)
    gasto = por_pedido.reindex(ok["order_id"]).groupby(ok["customer_id"].to_numpy()).sum()
    fechas = ok.loc[ok["order_date"].dt.year == 2025, "order_date"]
    return importes, gasto, fechas


def test_resumen_claves_y_cifras(ns):
    """resumen_numerico devuelve media 301,7, mediana 180,2 y asimetría 3,02 para los importes"""
    importes, _, _ = _datos()
    r = ns["resumen_numerico"](importes)
    assert set(r) == {"n", "media", "mediana", "p10", "p90", "p99", "asimetria"}, f"Claves: {sorted(r)}"
    assert r["n"] == 377145, f"n = {r['n']}"
    assert abs(r["media"] - 301.7) < 0.15 and abs(r["mediana"] - 180.2) < 0.15, f"Resumen: {r}"
    assert abs(r["p10"] - 28.0) < 0.15 and abs(r["p90"] - 717.6) < 0.15 and abs(r["p99"] - 1766.4) < 0.15, f"Resumen: {r}"
    assert abs(r["asimetria"] - 3.02) < 0.011, f"Asimetría: {r['asimetria']}"


def test_pareto(ns):
    """concentracion_pareto: el 20 % de clientes suma el 51,9 % del gasto"""
    _, gasto, _ = _datos()
    r = ns["concentracion_pareto"](gasto)
    assert set(r) == {0.01, 0.10, 0.20}, f"Claves: {sorted(r)}"
    assert abs(r[0.01] - 5.0) < 0.11 and abs(r[0.10] - 32.4) < 0.11 and abs(r[0.20] - 51.9) < 0.11, f"Pareto: {r}"


def test_semana(ns):
    """pedidos_por_dia_semana: viernes y sábado superan a los días de entre semana"""
    _, _, fechas = _datos()
    r = ns["pedidos_por_dia_semana"](fechas)
    assert list(r.index) == [0, 1, 2, 3, 4, 5, 6], f"Índice: {list(r.index)}"
    assert r.loc[4] > r.loc[0] and r.loc[5] > r.loc[0] and r.loc[6] < r.loc[0], f"Serie: {r.to_dict()}"
    assert [int(v) for v in r.tolist()] == [437, 443, 437, 434, 464, 462, 423], f"Serie: {r.tolist()}"


def test_hidden_otros_datos(ns):
    """Funciona con otros datos y con una serie pequeña (test oculto)"""
    importes, gasto, fechas = _datos(variant=True)
    r = ns["resumen_numerico"](importes)
    assert abs(r["mediana"] - round(float(np.median(importes)), 1)) < 0.11, f"Mediana: {r['mediana']}"
    p = ns["concentracion_pareto"](gasto, fracciones=(0.5,))
    esperado = gasto.sort_values(ascending=False).head(int(len(gasto) * 0.5)).sum() / gasto.sum() * 100
    assert abs(p[0.5] - esperado) < 0.11, f"Pareto 50 %: {p}"
    peq = pd.Series(pd.to_datetime(["2025-01-06", "2025-01-06", "2025-01-13", "2025-01-07"]))
    s = ns["pedidos_por_dia_semana"](peq)
    assert s.loc[0] == 2 and s.loc[1] == 1, f"Lunes: 3 pedidos en 2 fechas (1,5 → 2); martes: 1. Obtenido {s.to_dict()}"
