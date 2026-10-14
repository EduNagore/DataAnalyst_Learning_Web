"""Arnés de evaluación: ejecuta el asistente sobre el conjunto de oro y compara RESULTADOS, no texto SQL."""

from __future__ import annotations

import math


def normalize(rows: list[tuple]) -> list[tuple]:
    """Filas comparables: números redondeados a 2 decimales, texto en minúsculas, orden independiente."""
    # TODO
    raise NotImplementedError


def same_result(expected: list[tuple], actual: list[tuple]) -> bool:
    """¿Los dos resultados contienen las mismas filas (ignorando orden y redondeos menores)?"""
    # TODO
    raise NotImplementedError


def classify(answerable: bool, expected: list[tuple] | None, actual: list[tuple] | None, error: str | None) -> str:
    """Categoría: 'correcta', 'resultado_distinto', 'error_ejecucion', 'abstencion_correcta' o 'abstencion_innecesaria'.

    `actual` es None y `error` es 'ABSTENCION' cuando el asistente se negó a responder.
    """
    # TODO
    raise NotImplementedError


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción."""
    # TODO
    raise NotImplementedError


__all__ = ["classify", "math", "normalize", "same_result", "wilson_interval"]
