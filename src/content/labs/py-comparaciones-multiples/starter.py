import itertools

import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

shipments = load_table("shipments")


def ajustar_bonferroni(p) -> np.ndarray:
    """p-valores ajustados por Bonferroni, en el orden de entrada."""
    # TODO
    ...


def ajustar_holm(p) -> np.ndarray:
    """p-valores ajustados por Holm (descendente), en el orden de entrada."""
    # TODO
    ...


def ajustar_bh(p) -> np.ndarray:
    """q-valores de Benjamini-Hochberg, en el orden de entrada."""
    # TODO
    ...


def comparar_transportistas(shipments: pd.DataFrame) -> pd.DataFrame:
    """Parejas de transportistas: a, b, dif_media, p, p_holm, p_bh (ordenado por p)."""
    # TODO
    ...


def simular_fwer(m: int, n_sim: int = 2000, alpha: float = 0.05, seed: int = 0) -> dict:
    """Fracción de simulaciones con al menos un rechazo cuando todas las nulas son ciertas."""
    # TODO
    ...


tabla = comparar_transportistas(shipments)
print(tabla.round(4).to_string(index=False))
print(simular_fwer(20))
