import math

import pandas as pd
from datakit.data import load_table
from scipy import stats

web_sessions = load_table("web_sessions")


def trafico_diario(web_sessions: pd.DataFrame, dias: int = 90) -> float:
    """Sesiones medias por día natural en los últimos `dias` días del dataset."""
    # TODO
    ...


def tamano_por_rama(p1: float, mde_rel: float, alpha: float = 0.05, potencia: float = 0.8) -> int:
    """Usuarios por rama para detectar un cambio relativo `mde_rel` sobre `p1`."""
    # TODO
    ...


def mde_alcanzable(p1: float, n_por_rama: float, alpha: float = 0.05, potencia: float = 0.8) -> float:
    """Efecto relativo mínimo detectable con `n_por_rama` usuarios por rama (bisección)."""
    # TODO
    ...


def plan(p1: float, mde_rel: float, trafico: float, ramas: int = 2) -> dict:
    """n_por_rama, dias y semanas (completas) necesarios con el tráfico diario dado."""
    # TODO
    ...


trafico = trafico_diario(web_sessions)
print("sesiones/día:", round(trafico, 1))
for mde in (0.08, 0.10, 0.20):
    print(f"+{mde:.0%}:", plan(0.054, mde, trafico))
for semanas in (1, 4, 8, 17):
    n = trafico * 7 * semanas / 2
    print(f"{semanas} semanas → MDE {mde_alcanzable(0.054, n):.1%}")
