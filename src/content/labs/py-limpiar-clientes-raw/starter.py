import re

import pandas as pd
from datakit.data import load_raw

raw = load_raw("customers")
print(raw.shape, raw["customer_id"].nunique())

REGIONES = [
    "Andalucía", "Aragón", "Asturias", "Canarias", "Cantabria", "Castilla y León",
    "Castilla-La Mancha", "Cataluña", "Comunidad Valenciana", "Extremadura", "Galicia",
    "Illes Balears", "Madrid", "Navarra", "País Vasco", "Región de Murcia",
]
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}
COLUMNAS = [
    "customer_id", "signup_date", "acquisition_channel", "region", "province", "segment",
    "marketing_consent",
]


def parsear_fecha(texto: str) -> pd.Timestamp:
    """Convierte AAAA-MM-DD, DD/MM/AAAA o «D de mes de AAAA» en una fecha."""
    # TODO
    ...


def limpiar_clientes(raw: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cliente, con las columnas COLUMNAS, ordenado por customer_id."""
    # TODO: normaliza región, convierte fechas, rellena provincia, deduplica y ordena.
    ...


print(limpiar_clientes(raw).head())
