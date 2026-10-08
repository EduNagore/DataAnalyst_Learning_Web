import re

import pandas as pd
from datakit.data import load_raw, load_table

raw = load_raw("orders")
customers = load_table("customers")
print(raw.shape, raw["order_id"].nunique())
print(raw.head(3))

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def parsear_fecha(texto: str) -> pd.Timestamp:
    """Convierte AAAA-MM-DD, DD/MM/AAAA o «D de mes de AAAA» en una fecha."""
    # TODO
    ...


def limpiar_pedidos(raw: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Una fila por pedido, ordenado por order_id, con las banderas cliente_valido y tienda_sin_id."""
    # TODO: fechas, importes, device 'n/a' en tienda, deduplicar y marcar problemas.
    ...


limpio = limpiar_pedidos(raw, customers)
print(len(limpio), round(limpio["shipping_cost"].sum(), 2))
