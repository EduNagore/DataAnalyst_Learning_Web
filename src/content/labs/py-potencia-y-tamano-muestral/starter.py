import math

import numpy as np
from datakit.data import load_table
from scipy import stats

metricas = load_table("experiment_metrics")
exp = metricas[(metricas["experiment_id"] == "exp-checkout-v2") & (metricas["metric_name"] == "conversion_rate")]
control = exp.loc[exp["variant"] == "control", "value"].to_numpy()
tratamiento = exp.loc[exp["variant"] == "tratamiento", "value"].to_numpy()


def welch_t(a, b) -> tuple[float, float, float]:
    """(t, grados de libertad, p-valor bilateral) del contraste de Welch de a frente a b."""
    # TODO
    ...


def tamano_muestra(p1: float, mde_rel: float, alpha: float = 0.05, potencia: float = 0.8) -> int:
    """Clientes por grupo para detectar un cambio relativo `mde_rel` sobre la proporción `p1`."""
    # TODO
    ...


def potencia(p1: float, mde_rel: float, n: int, alpha: float = 0.05) -> float:
    """Potencia analítica de la comparación de dos proporciones con n por grupo."""
    # TODO
    ...


def potencia_simulada(
    p1: float, mde_rel: float, n: int, alpha: float = 0.05, n_sim: int = 4000, seed: int = 0
) -> float:
    """Fracción de simulaciones en las que se rechaza H0."""
    # TODO
    ...


t, gl, p = welch_t(tratamiento, control)
print(f"t = {t:.2f}, gl = {gl:.1f}, p = {p:.2e}")
print("n por grupo (+8 % sobre 5,4 %):", tamano_muestra(0.054, 0.08))
print("potencia con 10.000 por grupo:", round(potencia(0.054, 0.08, 10000), 3))
print("potencia simulada:", round(potencia_simulada(0.054, 0.08, 10000), 3))
