import math

import numpy as np
from datakit.data import load_table
from scipy import stats

metricas = load_table("experiment_metrics")
exp = metricas[(metricas["experiment_id"] == "exp-checkout-v2") & (metricas["metric_name"] == "conversion_rate")]
control = exp.loc[exp["variant"] == "control", "value"].to_numpy()
tratamiento = exp.loc[exp["variant"] == "tratamiento", "value"].to_numpy()


def welch_t(a, b) -> tuple[float, float, float]:
    """(t, grados de libertad, p-valor bilateral) del contraste de Welch de a frente a b."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    t = (a.mean() - b.mean()) / se
    gl = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    p = 2 * stats.t.sf(abs(t), gl)
    return float(t), float(gl), float(p)


def tamano_muestra(p1: float, mde_rel: float, alpha: float = 0.05, potencia: float = 0.8) -> int:
    """Clientes por grupo para detectar un cambio relativo `mde_rel` sobre la proporción `p1`."""
    p2 = p1 * (1 + mde_rel)
    za = stats.norm.ppf(1 - alpha / 2)
    zb = stats.norm.ppf(potencia)
    n = (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
    return math.ceil(n)


def potencia(p1: float, mde_rel: float, n: int, alpha: float = 0.05) -> float:
    """Potencia analítica de la comparación de dos proporciones con n por grupo."""
    p2 = p1 * (1 + mde_rel)
    se = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n)
    za = stats.norm.ppf(1 - alpha / 2)
    z = abs(p2 - p1) / se
    return float(stats.norm.cdf(z - za) + stats.norm.cdf(-z - za))


def potencia_simulada(
    p1: float, mde_rel: float, n: int, alpha: float = 0.05, n_sim: int = 4000, seed: int = 0
) -> float:
    """Fracción de simulaciones en las que se rechaza H0."""
    p2 = p1 * (1 + mde_rel)
    rng = np.random.default_rng(seed)
    x1 = rng.binomial(n, p1, size=n_sim)
    x2 = rng.binomial(n, p2, size=n_sim)
    ph1, ph2 = x1 / n, x2 / n
    pooled = (x1 + x2) / (2 * n)
    se = np.sqrt(pooled * (1 - pooled) * 2 / n)
    z = (ph2 - ph1) / se
    return float(np.mean(np.abs(z) > stats.norm.ppf(1 - alpha / 2)))


t, gl, p = welch_t(tratamiento, control)
print(f"t = {t:.2f}, gl = {gl:.1f}, p = {p:.2e}")
print("n por grupo (+8 % sobre 5,4 %):", tamano_muestra(0.054, 0.08))
print("potencia con 10.000 por grupo:", round(potencia(0.054, 0.08, 10000), 3))
print("potencia simulada:", round(potencia_simulada(0.054, 0.08, 10000), 3))
