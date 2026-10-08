import pandas as pd
from datakit.data import load_table

shipments = load_table("shipments")
retraso = (shipments["actual_date"] - shipments["promised_date"]).dt.days
print(len(retraso), retraso.min(), retraso.max())


def resumen_retrasos(x: pd.Series) -> dict:
    """n, media y desviacion (2 dec.); mediana, iqr, p90, p95 y p99 (1 dec.)."""
    # TODO
    ...


def cumple_sla(x: pd.Series, max_dias: int) -> float:
    """% de envíos con retraso <= max_dias (1 decimal)."""
    # TODO
    ...


def media_ponderada(tasas: list[float], pesos: list[float]) -> float:
    """Media de las tasas ponderada por los pesos (3 decimales)."""
    # TODO
    ...


print(resumen_retrasos(retraso))
print(cumple_sla(retraso, 0), cumple_sla(retraso, 4))
print(media_ponderada([7.881, 2.383], [149907, 180170]))
