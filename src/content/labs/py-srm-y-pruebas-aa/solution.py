import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

assignments = load_table("experiment_assignments")


def srm_chi2(control: int, tratamiento: int, reparto: tuple = (0.5, 0.5)) -> tuple[float, float]:
    """(chi2, p) del contraste de bondad de ajuste del reparto entre ramas."""
    total = control + tratamiento
    esperado = np.array([total * reparto[0], total * reparto[1]])
    observado = np.array([control, tratamiento])
    chi2 = float(((observado - esperado) ** 2 / esperado).sum())
    return chi2, float(stats.chi2.sf(chi2, df=1))


def srm_todos(assignments: pd.DataFrame, umbral: float = 0.001) -> pd.DataFrame:
    """experiment_id, control, tratamiento, pct_tratamiento, chi2, p, srm (ordenado por p)."""
    conteo = pd.crosstab(assignments["experiment_id"], assignments["variant"])
    filas = []
    for exp_id, fila in conteo.iterrows():
        chi2, p = srm_chi2(int(fila["control"]), int(fila["tratamiento"]))
        total = fila["control"] + fila["tratamiento"]
        filas.append(
            {
                "experiment_id": exp_id,
                "control": int(fila["control"]),
                "tratamiento": int(fila["tratamiento"]),
                "pct_tratamiento": 100 * fila["tratamiento"] / total,
                "chi2": chi2,
                "p": p,
                "srm": p < umbral,
            }
        )
    return pd.DataFrame(filas).sort_values("p", ignore_index=True)


def simular_aa(n_exp: int = 4000, n_por_rama: int = 5000, p: float = 0.054, seed: int = 0) -> dict:
    """Tasa de «significativos» (α = 0,05) y de SRM (p < 0,001) en pruebas A/A sin problemas."""
    rng = np.random.default_rng(seed)
    # SRM: la asignación aleatoria 50/50 de 2n usuarios
    n_total = 2 * n_por_rama
    control = rng.binomial(n_total, 0.5, size=n_exp)
    tratamiento = n_total - control
    esperado = n_total / 2
    chi2 = ((control - esperado) ** 2 + (tratamiento - esperado) ** 2) / esperado
    srm = (stats.chi2.sf(chi2, df=1) < 0.001).mean()
    # Métrica: dos ramas idénticas con conversión p
    xa = rng.binomial(n_por_rama, p, size=n_exp)
    xb = rng.binomial(n_por_rama, p, size=n_exp)
    pooled = (xa + xb) / (2 * n_por_rama)
    se = np.sqrt(pooled * (1 - pooled) * 2 / n_por_rama)
    z = (xb - xa) / n_por_rama / se
    signif = (np.abs(z) > stats.norm.ppf(0.975)).mean()
    return {"signif_05": float(signif), "srm_001": float(srm)}


tabla = srm_todos(assignments)
print(tabla.round(4).to_string(index=False))
print(simular_aa())
