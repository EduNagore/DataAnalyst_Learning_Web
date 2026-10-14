import pandas as pd
from datakit.data import load_table

fuente = load_table("orders")


def marca_de_agua(destino: pd.DataFrame, columna: str):
    """Valor máximo de `columna` en el destino (None si está vacío): hasta dónde hemos cargado."""
    # TODO
    ...


def extraer(fuente: pd.DataFrame, columna: str, desde) -> pd.DataFrame:
    """Filas de la fuente con `columna` >= `desde` (todas si `desde` es None)."""
    # TODO
    ...


def cargar(destino: pd.DataFrame, lote: pd.DataFrame, clave: str) -> pd.DataFrame:
    """Upsert por clave: las filas del lote sustituyen a las del destino con la misma clave y las nuevas se añaden.
    El resultado queda ordenado por clave y sin duplicados."""
    # TODO
    ...


def sincronizar(fuente, destino, columna: str, clave: str, solape=None):
    """Una ejecución incremental: lee desde la marca de agua menos un solape (por defecto 1 día; para recoger filas tardías),
    hace upsert y devuelve (destino_nuevo, resumen) con `leidas`, `nuevas` y `actualizadas`."""
    # TODO
    ...


vacio = fuente.iloc[0:0]
hasta_2025 = fuente[fuente["order_date"] < "2026-01-01"]
d1, r1 = sincronizar(hasta_2025, vacio, "order_date", "order_id")
d2, r2 = sincronizar(fuente, d1, "order_date", "order_id")
d3, r3 = sincronizar(fuente, d2, "order_date", "order_id")
print("carga inicial:", r1, "| segunda carga:", r2, "| repetición:", r3)
print("filas destino:", len(d3), "= filas fuente:", len(fuente))
