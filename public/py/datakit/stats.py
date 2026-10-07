"""Ayudas estadísticas mínimas para que los labs se centren en el concepto.

No sustituyen a scipy/statsmodels: son atajos pequeños y legibles.
"""

import math


def proportion_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianza (aprox. normal) para una proporción."""
    if n <= 0:
        raise ValueError("n debe ser positivo")
    p = successes / n
    half = z * math.sqrt(p * (1 - p) / n)
    return p - half, p + half
