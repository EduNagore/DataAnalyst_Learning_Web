import pandas as pd
from datakit.data import load_table

subs = load_table("subscriptions")


def mrr_mensual(subs: pd.DataFrame) -> pd.DataFrame:
    """Cascada mensual de MRR (mes = Period mensual): `mrr_inicial` (MRR activo al cerrar el mes anterior),
    `nuevo` (altas del mes), `churn` (bajas del mes), `mrr` (MRR activo al cerrar el mes), `suscripciones`
    activas al cierre y `bajas` (número). Una suscripción está activa al cierre de un mes si empezó antes
    o durante el mes y no se ha cancelado hasta el último día del mes incluido."""
    s = subs.assign(inicio=pd.to_datetime(subs["started_at"]), fin=pd.to_datetime(subs["cancelled_at"]))
    ultimo_mes = max(s["inicio"].max(), s["fin"].max()).to_period("M")
    meses = pd.period_range(s["inicio"].min().to_period("M"), ultimo_mes, freq="M")
    filas = []
    for m in meses:
        ultimo = m.end_time.normalize()
        activa = (s["inicio"] <= ultimo) & (s["fin"].isna() | (s["fin"] > ultimo))
        nuevas = s["inicio"].dt.to_period("M") == m
        bajas = s["fin"].dt.to_period("M") == m
        filas.append(
            {
                "mes": m,
                "nuevo": float(s.loc[nuevas, "mrr_eur"].sum()),
                "churn": float(s.loc[bajas, "mrr_eur"].sum()),
                "mrr": float(s.loc[activa, "mrr_eur"].sum()),
                "suscripciones": int(activa.sum()),
                "bajas": int(bajas.sum()),
            }
        )
    t = pd.DataFrame(filas).set_index("mes")
    t.insert(0, "mrr_inicial", t["mrr"].shift(1).fillna(0.0))
    return t


def churn_de_ingresos(wf: pd.DataFrame) -> pd.Series:
    """Churn de MRR de cada mes: bajas / MRR inicial (en %)."""
    return 100 * wf["churn"] / wf["mrr_inicial"].where(wf["mrr_inicial"] > 0)


def ratio_rapido_mrr(wf: pd.DataFrame) -> pd.Series:
    """MRR nuevo / MRR perdido de cada mes."""
    return wf["nuevo"] / wf["churn"].where(wf["churn"] > 0)


def retencion_de_ingresos(subs: pd.DataFrame, inicio: str, fin: str) -> dict:
    """Con las suscripciones activas al cierre de `inicio` (cohorte), devuelve el porcentaje de MRR y de
    suscripciones que siguen activas al cierre de `fin`: grr, nrr (sin ampliaciones coincide con grr) y logos."""
    a, b = pd.Timestamp(inicio), pd.Timestamp(fin)
    s = subs.assign(inicio=pd.to_datetime(subs["started_at"]), fin=pd.to_datetime(subs["cancelled_at"]))
    cohorte = s[(s["inicio"] <= a) & (s["fin"].isna() | (s["fin"] > a))]
    siguen = cohorte[cohorte["fin"].isna() | (cohorte["fin"] > b)]
    grr = 100 * siguen["mrr_eur"].sum() / cohorte["mrr_eur"].sum()
    return {"grr": float(grr), "nrr": float(grr), "logos": float(100 * len(siguen) / len(cohorte))}


wf = mrr_mensual(subs)
cierre = wf.loc[:"2026-05"]
print(cierre.tail(3).round(0))
print("churn de MRR (mayo 2026):", round(churn_de_ingresos(cierre).iloc[-1], 2), "%")
print("ratio rápido (mayo 2026):", round(ratio_rapido_mrr(cierre).iloc[-1], 2))
print("ARR (mayo 2026):", round(12 * cierre["mrr"].iloc[-1]))
print(retencion_de_ingresos(subs, "2025-05-31", "2026-05-31"))
