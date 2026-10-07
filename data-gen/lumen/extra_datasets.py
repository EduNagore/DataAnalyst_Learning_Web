"""Datasets externos pequeños para `public/data/extra/` (ver docs/DATASET.md §6).

No son sintéticos: son copias verificadas de datasets de referencia muy
conocidos, obtenidas de una fuente pública en el momento de construir este
generador y guardadas en `vendor/` para que la generación no dependa de
red. Fuentes exactas en `docs/SOURCES.md`.

- `anscombe.csv`: el cuarteto de Anscombe (Anscombe, 1973), vía el dataset
  "anscombe" de seaborn (mwaskom/seaborn-data).
- `datasaurus_dozen.csv`: el Datasaurus Dozen (Matejka & Fitzmaurice, 2017;
  conjunto original de Alberto Cairo), vía el paquete R `datasauRus`
  (jumpingrivers/datasauRus).
- `airline_passengers.csv`: la serie mensual de pasajeros aéreos de
  Box & Jenkins (1976), vía jbrownlee/Datasets.
"""

from pathlib import Path

import pandas as pd

_VENDOR_DIR = Path(__file__).parent / "vendor"


def load_extra_datasets() -> dict[str, pd.DataFrame]:
    return {
        "anscombe": pd.read_csv(_VENDOR_DIR / "anscombe.csv"),
        "datasaurus_dozen": pd.read_csv(_VENDOR_DIR / "datasaurus_dozen.csv"),
        "airline_passengers": pd.read_csv(_VENDOR_DIR / "airline_passengers.csv"),
    }
