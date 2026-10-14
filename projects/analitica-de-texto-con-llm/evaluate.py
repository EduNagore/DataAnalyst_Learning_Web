"""Evaluación contra etiquetas humanas. Implementa los TODO y haz pasar `pytest`."""

from __future__ import annotations

import numpy as np


def confusion(y_true: list[str], y_pred: list[str], classes: list[str]) -> np.ndarray:
    """Matriz de confusión (filas = real, columnas = predicha) en el orden de `classes`."""
    # TODO
    raise NotImplementedError


def precision_recall_f1(matrix: np.ndarray) -> dict[str, np.ndarray]:
    """Precisión, exhaustividad y F1 por clase (0 si el denominador es 0)."""
    # TODO
    raise NotImplementedError


def cohen_kappa(matrix: np.ndarray) -> float:
    """κ = (po - pe) / (1 - pe)."""
    # TODO
    raise NotImplementedError


def sample_size(margin: float, p: float = 0.5, z: float = 1.96) -> int:
    """Casos a etiquetar para estimar una proporción con el margen de error indicado."""
    # TODO
    raise NotImplementedError
