import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
print(orders.head())
print(orders.dtypes)


def pedidos_por_canal_y_anio(orders: pd.DataFrame) -> pd.DataFrame:
    """Pedidos por año y canal: columnas `anio`, `channel`, `pedidos`."""
    # TODO: agrupa por año (de order_date) y canal, y cuenta los pedidos.
    ...


def marcar_envio_gratis(orders: pd.DataFrame) -> pd.DataFrame:
    """Copia de `orders` con la columna booleana `envio_gratis`. No modifica el original."""
    # TODO
    ...
