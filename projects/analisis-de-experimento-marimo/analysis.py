"""Funciones del análisis del experimento. Implementa los TODO y haz pasar `pytest`."""

from __future__ import annotations

import numpy as np
from scipy import stats


def srm_pvalue(observed: list[int], expected_ratio: list[float]) -> float:
    """p-valor del chi-cuadrado de bondad de ajuste entre el reparto observado y el diseñado.

    observed: usuarios por variante, p. ej. [50_400, 49_600]
    expected_ratio: reparto diseñado, p. ej. [0.5, 0.5]
    """
    # TODO: calcula los esperados (total * ratio) y usa scipy.stats.chisquare.
    raise NotImplementedError


def cuped_adjust(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """Ajuste CUPED: y' = y - theta * (x - mean(x)), con theta = cov(x, y) / var(x).

    Devuelve (y_ajustada, theta). La covariable x debe ser PREVIA al experimento.
    """
    # TODO
    raise NotImplementedError


def diff_in_means(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> dict:
    """Diferencia de medias (b - a) con intervalo de confianza de Welch.

    Devuelve {"diff": ..., "low": ..., "high": ..., "p_value": ...}.
    """
    # TODO: usa scipy.stats.ttest_ind(..., equal_var=False) y el error estándar de Welch.
    raise NotImplementedError


def sample_size_two_proportions(p: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Tamaño de muestra por grupo para detectar una diferencia absoluta `delta` en una proporción base `p`."""
    # TODO: fórmula con la normal estándar; devuelve un entero (redondea hacia arriba).
    raise NotImplementedError


def holm_adjust(pvalues: list[float]) -> list[float]:
    """p-valores ajustados por Holm (control del error por familia), en el mismo orden de entrada."""
    # TODO
    raise NotImplementedError


__all__ = ["cuped_adjust", "diff_in_means", "holm_adjust", "sample_size_two_proportions", "srm_pvalue", "stats"]
