import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

assignments = load_table("experiment_assignments")


def srm_chi2(control: int, tratamiento: int, reparto: tuple = (0.5, 0.5)) -> tuple[float, float]:
    """(chi2, p) del contraste de bondad de ajuste del reparto entre ramas."""
    # TODO
    ...


def srm_todos(assignments: pd.DataFrame, umbral: float = 0.001) -> pd.DataFrame:
    """experiment_id, control, tratamiento, pct_tratamiento, chi2, p, srm (ordenado por p)."""
    # TODO
    ...


def simular_aa(n_exp: int = 4000, n_por_rama: int = 5000, p: float = 0.054, seed: int = 0) -> dict:
    """Tasa de «significativos» (α = 0,05) y de SRM (p < 0,001) en pruebas A/A sin problemas."""
    # TODO
    ...


tabla = srm_todos(assignments)
print(tabla.round(4).to_string(index=False))
print(simular_aa())
