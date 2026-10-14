"""Validación de origen móvil y métricas de previsión. Implementa los TODO y haz pasar `pytest`."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

Forecaster = Callable[[pd.Series, int], np.ndarray]


def seasonal_naive(history: pd.Series, horizon: int, season: int = 7) -> np.ndarray:
    """Previsión ingenua estacional: repite los últimos `season` valores hasta cubrir el horizonte."""
    # TODO
    raise NotImplementedError


def rolling_origins(n: int, horizon: int, n_origins: int, min_train: int) -> list[int]:
    """Posiciones (índice del primer punto a predecir) de los orígenes móviles, sin solapar el futuro con el entrenamiento.

    Devuelve n_origins posiciones equiespaciadas por `horizon`, la última de las cuales deja exactamente `horizon` puntos
    de evaluación al final de la serie. La primera debe ser >= min_train.
    """
    # TODO
    raise NotImplementedError


def wape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Error absoluto ponderado: sum|y - f| / sum|y|."""
    # TODO
    raise NotImplementedError


def bias(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Sesgo relativo: sum(f - y) / sum(y). Positivo = sobreestima."""
    # TODO
    raise NotImplementedError


def interval_coverage(actual: np.ndarray, low: np.ndarray, high: np.ndarray) -> float:
    """Proporción de valores reales dentro del intervalo [low, high]."""
    # TODO
    raise NotImplementedError


def backtest(series: pd.Series, forecaster: Forecaster, horizon: int, n_origins: int, min_train: int) -> pd.DataFrame:
    """Ejecuta `forecaster(historia, horizonte)` en cada origen y devuelve una fila por origen con wape y bias.

    IMPORTANTE: el modelo solo ve datos ANTERIORES al origen (sin fuga de información).
    """
    # TODO
    raise NotImplementedError
