import pandas as pd
from datakit.data import load_table

shipments = load_table("shipments")
retraso = (shipments["actual_date"] - shipments["promised_date"]).dt.days
print(len(retraso), retraso.min(), retraso.max())


def resumen_retrasos(x: pd.Series) -> dict:
    """n, media y desviacion (2 dec.); mediana, iqr, p90, p95 y p99 (1 dec.)."""
    return {
        "n": int(x.notna().sum()),
        "media": round(float(x.mean()), 2),
        "mediana": round(float(x.median()), 1),
        "desviacion": round(float(x.std()), 2),
        "iqr": round(float(x.quantile(0.75) - x.quantile(0.25)), 1),
        "p90": round(float(x.quantile(0.90)), 1),
        "p95": round(float(x.quantile(0.95)), 1),
        "p99": round(float(x.quantile(0.99)), 1),
    }


def cumple_sla(x: pd.Series, max_dias: int) -> float:
    """% de envíos con retraso <= max_dias (1 decimal)."""
    return round(float((x <= max_dias).mean() * 100), 1)


def media_ponderada(tasas: list[float], pesos: list[float]) -> float:
    """Media de las tasas ponderada por los pesos (3 decimales)."""
    return round(sum(t * w for t, w in zip(tasas, pesos, strict=True)) / sum(pesos), 3)


print(resumen_retrasos(retraso))
print(cumple_sla(retraso, 0), cumple_sla(retraso, 4))
print(media_ponderada([7.881, 2.383], [149907, 180170]))
