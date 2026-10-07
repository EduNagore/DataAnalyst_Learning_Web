import pandas as pd
from datakit.data import load_table

orders = load_table("orders")


def pedidos_por_canal_y_anio(orders: pd.DataFrame) -> pd.DataFrame:
    """Pedidos por año y canal: columnas `anio`, `channel`, `pedidos`."""
    anio = orders["order_date"].dt.year.rename("anio")
    return orders.groupby([anio, "channel"]).size().reset_index(name="pedidos")


def marcar_envio_gratis(orders: pd.DataFrame) -> pd.DataFrame:
    """Copia de `orders` con la columna booleana `envio_gratis`. No modifica el original."""
    # `assign` devuelve un DataFrame nuevo: el que nos pasan queda intacto.
    return orders.assign(envio_gratis=orders["shipping_cost"] == 0)
