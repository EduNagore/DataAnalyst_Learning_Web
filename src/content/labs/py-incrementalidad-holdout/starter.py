import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

metricas = load_table("experiment_metrics")
ID = "exp-social-ads-geo-holdout"


def serie(metricas: pd.DataFrame, experimento: str, metrica: str, variante: str) -> np.ndarray:
    """Valores diarios, ordenados por fecha, de una métrica y una variante de un experimento."""
    # TODO
    ...


def lift_holdout(tratamiento: np.ndarray, control: np.ndarray) -> dict:
    """Lift relativo (tratamiento / control − 1) con IC 95 % de Welch (diferencia entre la media del control)
    y p-valor bilateral. Devuelve lift, ic_bajo, ic_alto y p."""
    # TODO
    ...


def fraccion_incremental(lift_real: float, lift_atribuido: float) -> float:
    """Parte del lift que dice la atribución que es realmente causal."""
    # TODO
    ...


def iroas(ingreso_incremental: float, gasto: float) -> float:
    """Ingreso incremental por euro gastado."""
    # TODO
    ...


real = lift_holdout(
    serie(metricas, ID, "revenue_per_user", "tratamiento"), serie(metricas, ID, "revenue_per_user", "control")
)
atrib = lift_holdout(
    serie(metricas, ID, "last_click_attributed_revenue_per_user", "tratamiento"),
    serie(metricas, ID, "last_click_attributed_revenue_per_user", "control"),
)
print("lift real (ingresos por usuario):", {k: round(v, 4) for k, v in real.items()})
print("lift atribuido (último clic):    ", {k: round(v, 4) for k, v in atrib.items()})
print("fracción incremental:", round(fraccion_incremental(real["lift"], atrib["lift"]), 3))
