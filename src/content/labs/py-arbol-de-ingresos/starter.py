import math

import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")


def arbol_ingresos(orders: pd.DataFrame, order_items: pd.DataFrame, anio: int) -> dict:
    """clientes_activos, pedidos, pedidos_por_cliente (3 dec.), ticket_medio e ingresos (2 dec.)."""
    # TODO: ingresos por pedido, filtro de año y de estado, y los cuatro factores.
    ...


def contribuciones(a: dict, b: dict) -> dict:
    """Reparto logarítmico del crecimiento de `ingresos` entre los tres factores (3 decimales)."""
    # TODO
    ...


a = arbol_ingresos(orders, order_items, 2024)
b = arbol_ingresos(orders, order_items, 2025)
print(a)
print(b)
print(contribuciones(a, b))
