import io

import pandas as pd
import pyarrow.parquet as pq
from datakit.data import load_table

orders = load_table("orders")


def a_csv(df: pd.DataFrame) -> bytes:
    """El DataFrame como texto CSV (UTF-8, sin índice)."""
    # TODO
    ...


def a_parquet(df: pd.DataFrame, filas_por_grupo: int = 50_000, compresion: str = "zstd") -> bytes:
    """El DataFrame como fichero Parquet en memoria, con grupos de filas del tamaño indicado."""
    # TODO
    ...


def bytes_por_columna(parquet: bytes) -> pd.Series:
    """Bytes comprimidos que ocupa cada columna en todo el fichero, de mayor a menor."""
    # TODO
    ...


def grupos_a_leer(parquet: bytes, columna: str, desde, hasta) -> list[int]:
    """Índices de los grupos de filas que pueden contener valores de `columna` entre `desde` y `hasta`
    (ambos incluidos), usando solo las estadísticas mínimo/máximo del pie del fichero."""
    # TODO
    ...


def fraccion_leida(parquet: bytes, columnas: list[str], grupos: list[int]) -> float:
    """Fracción de los bytes comprimidos del fichero que hay que leer para las `columnas` en esos `grupos`."""
    # TODO
    ...


ordenado = orders.sort_values("order_date").reset_index(drop=True)
desordenado = orders.sort_values("customer_id").reset_index(drop=True)
pq_ord, pq_des = a_parquet(ordenado), a_parquet(desordenado)
print("CSV:", round(len(a_csv(ordenado)) / 1e6, 1), "MB | Parquet:", round(len(pq_ord) / 1e6, 1), "MB")
print(bytes_por_columna(pq_ord).head(3).to_dict())
g1, g2 = grupos_a_leer(pq_ord, "order_date", "2026-03-01", "2026-03-31"), grupos_a_leer(pq_des, "order_date", "2026-03-01", "2026-03-31")
print("grupos a leer (ordenado por fecha):", g1, "| (ordenado por cliente):", g2)
print("fracción leída:", round(fraccion_leida(pq_ord, ["order_date", "status"], g1), 4))
