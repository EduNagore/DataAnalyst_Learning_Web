import math

import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")


def arbol_ingresos(orders: pd.DataFrame, order_items: pd.DataFrame, anio: int) -> dict:
    """clientes_activos, pedidos, pedidos_por_cliente (3 dec.), ticket_medio e ingresos (2 dec.)."""
    por_pedido = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    ok = orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == anio)]
    ingresos = float(por_pedido.reindex(ok["order_id"]).sum())
    pedidos = len(ok)
    clientes = int(ok["customer_id"].nunique())
    return {
        "clientes_activos": clientes,
        "pedidos": pedidos,
        "pedidos_por_cliente": round(pedidos / clientes, 3),
        "ticket_medio": round(ingresos / pedidos, 2),
        "ingresos": round(ingresos, 2),
    }


def contribuciones(a: dict, b: dict) -> dict:
    """Reparto logarítmico del crecimiento de `ingresos` entre los tres factores (3 decimales)."""
    total = math.log(b["ingresos"] / a["ingresos"])
    factores = ["clientes_activos", "pedidos_por_cliente", "ticket_medio"]
    return {f: round(math.log(b[f] / a[f]) / total, 3) for f in factores}


a = arbol_ingresos(orders, order_items, 2024)
b = arbol_ingresos(orders, order_items, 2025)
print(a)
print(b)
print(contribuciones(a, b))
