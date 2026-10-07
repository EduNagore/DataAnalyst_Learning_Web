"""Carga de las tablas de Lumen como DataFrames de pandas.

En el navegador, el worker de Pyodide escribe los Parquet en `/data/...` antes
de ejecutar el código del alumno. En CPython (tests), `DATA_ROOT` apunta a
`public/data` (se fija con `set_data_root`).
"""

from pathlib import Path

import pandas as pd

DATA_ROOT = Path("/data")


def set_data_root(path) -> None:
    global DATA_ROOT
    DATA_ROOT = Path(path)


def load_table(name: str, variant: bool = False) -> pd.DataFrame:
    """Tabla de `lumen/` (o de `lumen_variant/` si variant=True)."""
    folder = "lumen_variant" if variant else "lumen"
    path = DATA_ROOT / folder / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"La tabla «{name}» no está disponible en este lab. "
            f"Comprueba que está en `datasets` del enunciado (buscada en {path})."
        )
    return pd.read_parquet(path)


def load_raw(name: str) -> pd.DataFrame:
    """Copia «sucia» de `lumen_raw/` (CSV), para los labs de limpieza."""
    return pd.read_csv(DATA_ROOT / "lumen_raw" / f"{name}.csv")


def load_extra(name: str) -> pd.DataFrame:
    """Datasets de referencia de `extra/` (anscombe, datasaurus_dozen, airline_passengers)."""
    return pd.read_csv(DATA_ROOT / "extra" / f"{name}.csv")
