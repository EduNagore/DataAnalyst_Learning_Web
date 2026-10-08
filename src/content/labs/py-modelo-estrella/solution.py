import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def construir_hechos(order_items: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Una fila por línea de pedido: order_item_id, order_id, customer_id, product_id, fecha_id, cantidad, importe, estado."""
    m = order_items.merge(
        orders[["order_id", "customer_id", "order_date", "status"]], on="order_id", how="left", validate="many_to_one"
    )
    fecha = m["order_date"]
    return pd.DataFrame(
        {
            "order_item_id": m["order_item_id"],
            "order_id": m["order_id"],
            "customer_id": m["customer_id"],
            "product_id": m["product_id"],
            "fecha_id": (fecha.dt.year * 10000 + fecha.dt.month * 100 + fecha.dt.day).astype("int64"),
            "cantidad": m["quantity"],
            "importe": m["quantity"] * m["unit_price"],
            "estado": m["status"],
        }
    )


def dim_fecha(fecha_min, fecha_max) -> pd.DataFrame:
    """Un día por fila, sin huecos: fecha_id, fecha, anio, mes, trimestre, dia_semana."""
    dias = pd.date_range(pd.Timestamp(fecha_min).normalize(), pd.Timestamp(fecha_max).normalize(), freq="D")
    return pd.DataFrame(
        {
            "fecha_id": (dias.year * 10000 + dias.month * 100 + dias.day).astype("int64"),
            "fecha": dias,
            "anio": dias.year,
            "mes": dias.month,
            "trimestre": dias.quarter,
            "dia_semana": dias.dayofweek,
        }
    )


def comprobar_integridad(hechos, dim_clientes, dim_productos, dim_fechas) -> dict:
    """Filas del hecho sin clave en su dimensión: clientes_huerfanos, productos_huerfanos, fechas_huerfanas."""
    return {
        "clientes_huerfanos": int((~hechos["customer_id"].isin(dim_clientes["customer_id"])).sum()),
        "productos_huerfanos": int((~hechos["product_id"].isin(dim_productos["product_id"])).sum()),
        "fechas_huerfanas": int((~hechos["fecha_id"].isin(dim_fechas["fecha_id"])).sum()),
    }


hechos = construir_hechos(order_items, orders)
fechas = dim_fecha(orders["order_date"].min(), orders["order_date"].max())
print(len(hechos), round(float(hechos["importe"].sum()), 2), len(fechas))
print(comprobar_integridad(hechos, customers, products, fechas))
