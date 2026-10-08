import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def construir_hechos(order_items: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Una fila por línea de pedido: order_item_id, order_id, customer_id, product_id, fecha_id, cantidad, importe, estado."""
    # TODO
    ...


def dim_fecha(fecha_min, fecha_max) -> pd.DataFrame:
    """Un día por fila, sin huecos: fecha_id, fecha, anio, mes, trimestre, dia_semana."""
    # TODO
    ...


def comprobar_integridad(hechos, dim_clientes, dim_productos, dim_fechas) -> dict:
    """Filas del hecho sin clave en su dimensión: clientes_huerfanos, productos_huerfanos, fechas_huerfanas."""
    # TODO
    ...


# Cuando las tres funciones estén listas, comprueba el modelo:
# hechos = construir_hechos(order_items, orders)
# fechas = dim_fecha(orders["order_date"].min(), orders["order_date"].max())
# print(len(hechos), round(float(hechos["importe"].sum()), 2), len(fechas))
# print(comprobar_integridad(hechos, customers, products, fechas))
