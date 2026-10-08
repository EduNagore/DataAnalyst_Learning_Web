import math

import pandas as pd
from datakit.data import load_table
from scipy import stats

web_sessions = load_table("web_sessions")


def trafico_diario(web_sessions: pd.DataFrame, dias: int = 90) -> float:
    """Sesiones medias por día natural en los últimos `dias` días del dataset."""
    dia = web_sessions["started_at"].dt.normalize()
    por_dia = dia.value_counts().sort_index()
    ultimo = por_dia.index.max()
    reciente = por_dia[por_dia.index > ultimo - pd.Timedelta(days=dias)]
    return float(reciente.mean())


def tamano_por_rama(p1: float, mde_rel: float, alpha: float = 0.05, potencia: float = 0.8) -> int:
    """Usuarios por rama para detectar un cambio relativo `mde_rel` sobre `p1`."""
    p2 = p1 * (1 + mde_rel)
    za = stats.norm.ppf(1 - alpha / 2)
    zb = stats.norm.ppf(potencia)
    n = (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
    return math.ceil(n)


def mde_alcanzable(p1: float, n_por_rama: float, alpha: float = 0.05, potencia: float = 0.8) -> float:
    """Efecto relativo mínimo detectable con `n_por_rama` usuarios por rama (bisección)."""
    lo, hi = 1e-6, 2.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if tamano_por_rama(p1, mid, alpha, potencia) > n_por_rama:
            lo = mid
        else:
            hi = mid
    return hi


def plan(p1: float, mde_rel: float, trafico: float, ramas: int = 2) -> dict:
    """n_por_rama, dias y semanas (completas) necesarios con el tráfico diario dado."""
    n = tamano_por_rama(p1, mde_rel)
    dias = math.ceil(ramas * n / trafico)
    return {"n_por_rama": n, "dias": dias, "semanas": math.ceil(dias / 7)}


trafico = trafico_diario(web_sessions)
print("sesiones/día:", round(trafico, 1))
for mde in (0.08, 0.10, 0.20):
    print(f"+{mde:.0%}:", plan(0.054, mde, trafico))
for semanas in (1, 4, 8, 17):
    n = trafico * 7 * semanas / 2
    print(f"{semanas} semanas → MDE {mde_alcanzable(0.054, n):.1%}")
