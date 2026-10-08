import itertools

import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

shipments = load_table("shipments")


def ajustar_bonferroni(p) -> np.ndarray:
    """p-valores ajustados por Bonferroni, en el orden de entrada."""
    p = np.asarray(p, dtype=float)
    return np.minimum(1.0, p * len(p))


def ajustar_holm(p) -> np.ndarray:
    """p-valores ajustados por Holm (descendente), en el orden de entrada."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    orden = np.argsort(p)
    escalado = p[orden] * (m - np.arange(m))
    ajustado = np.minimum(1.0, np.maximum.accumulate(escalado))
    out = np.empty(m)
    out[orden] = ajustado
    return out


def ajustar_bh(p) -> np.ndarray:
    """q-valores de Benjamini-Hochberg, en el orden de entrada."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    orden = np.argsort(p)
    escalado = p[orden] * m / (np.arange(m) + 1)
    ajustado = np.minimum(1.0, np.minimum.accumulate(escalado[::-1])[::-1])
    out = np.empty(m)
    out[orden] = ajustado
    return out


def comparar_transportistas(shipments: pd.DataFrame) -> pd.DataFrame:
    """Parejas de transportistas: a, b, dif_media, p, p_holm, p_bh (ordenado por p)."""
    retraso = (shipments["actual_date"] - shipments["promised_date"]).dt.days
    grupos = {c: retraso[shipments["carrier"] == c].to_numpy() for c in sorted(shipments["carrier"].unique())}
    filas = []
    for a, b in itertools.combinations(grupos, 2):
        p = stats.mannwhitneyu(grupos[a], grupos[b], alternative="two-sided").pvalue
        filas.append({"a": a, "b": b, "dif_media": grupos[a].mean() - grupos[b].mean(), "p": p})
    out = pd.DataFrame(filas)
    out["p_holm"] = ajustar_holm(out["p"])
    out["p_bh"] = ajustar_bh(out["p"])
    return out.sort_values("p", ignore_index=True)


def simular_fwer(m: int, n_sim: int = 2000, alpha: float = 0.05, seed: int = 0) -> dict:
    """Fracción de simulaciones con al menos un rechazo cuando todas las nulas son ciertas."""
    rng = np.random.default_rng(seed)
    p = rng.random((n_sim, m))
    sin = (p < alpha).any(axis=1).mean()
    bonf = (np.array([ajustar_bonferroni(f) for f in p]) < alpha).any(axis=1).mean()
    bh = (np.array([ajustar_bh(f) for f in p]) < alpha).any(axis=1).mean()
    return {"sin_correccion": float(sin), "bonferroni": float(bonf), "bh": float(bh)}


tabla = comparar_transportistas(shipments)
print(tabla.round(4).to_string(index=False))
print(simular_fwer(20))
