import pandas as pd
from datakit.data import load_table

subs = load_table("subscriptions")


def mrr_mensual(subs: pd.DataFrame) -> pd.DataFrame:
    """Cascada mensual de MRR (mes = Period mensual): `mrr_inicial` (MRR activo al cerrar el mes anterior),
    `nuevo` (altas del mes), `churn` (bajas del mes), `mrr` (MRR activo al cerrar el mes), `suscripciones`
    activas al cierre y `bajas` (número). Una suscripción está activa al cierre de un mes si empezó antes
    o durante el mes y no se ha cancelado hasta el último día del mes incluido."""
    # TODO
    ...


def churn_de_ingresos(wf: pd.DataFrame) -> pd.Series:
    """Churn de MRR de cada mes: bajas / MRR inicial (en %)."""
    # TODO
    ...


def ratio_rapido_mrr(wf: pd.DataFrame) -> pd.Series:
    """MRR nuevo / MRR perdido de cada mes."""
    # TODO
    ...


def retencion_de_ingresos(subs: pd.DataFrame, inicio: str, fin: str) -> dict:
    """Con las suscripciones activas al cierre de `inicio` (cohorte), devuelve el porcentaje de MRR y de
    suscripciones que siguen activas al cierre de `fin`: grr, nrr (sin ampliaciones coincide con grr) y logos."""
    # TODO
    ...


wf = mrr_mensual(subs)
cierre = wf.loc[:"2026-05"]
print(cierre.tail(3).round(0))
print("churn de MRR (mayo 2026):", round(churn_de_ingresos(cierre).iloc[-1], 2), "%")
print("ratio rápido (mayo 2026):", round(ratio_rapido_mrr(cierre).iloc[-1], 2))
print("ARR (mayo 2026):", round(12 * cierre["mrr"].iloc[-1]))
print(retencion_de_ingresos(subs, "2025-05-31", "2026-05-31"))
