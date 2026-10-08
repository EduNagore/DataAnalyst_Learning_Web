import numpy as np
from datakit.data import load_table
from scipy import stats

metricas = load_table("experiment_metrics")
experimentos = load_table("experiments")


def simular_peeking(revisiones: int, n_sim: int = 20000, seed: int = 0, limites=None) -> float:
    """Fracción de A/A con algún |Z_k| por encima del límite en alguna revisión."""
    rng = np.random.default_rng(seed)
    z = np.cumsum(rng.standard_normal((n_sim, revisiones)), axis=1) / np.sqrt(np.arange(1, revisiones + 1))
    umbral = np.full(revisiones, 1.96) if limites is None else np.asarray(limites, dtype=float)
    return float(np.mean((np.abs(z) > umbral[None, :]).any(axis=1)))


def limites_obf(revisiones: int, c: float) -> np.ndarray:
    """Límites tipo O'Brien-Fleming: c * sqrt(K / k) para k = 1..K."""
    return c * np.sqrt(revisiones / np.arange(1, revisiones + 1))


def simular_msprt(
    n_obs: int = 2000,
    n_sim: int = 3000,
    tau2: float = 0.25,
    alpha: float = 0.05,
    efecto: float = 0.0,
    seed: int = 0,
) -> float:
    """Fracción de simulaciones en las que el mSPRT alcanza Λ ≥ 1/alpha en algún momento."""
    rng = np.random.default_rng(seed)
    datos = rng.standard_normal((n_sim, n_obs)) + efecto
    n = np.arange(1, n_obs + 1)
    xbar = np.cumsum(datos, axis=1) / n
    sigma2 = 1.0
    log_lambda = 0.5 * np.log(sigma2 / (sigma2 + n * tau2)) + n**2 * tau2 * xbar**2 / (2 * sigma2 * (sigma2 + n * tau2))
    return float(np.mean((log_lambda >= np.log(1 / alpha)).any(axis=1)))


def primer_cruce(control, tratamiento, minimo: int = 5):
    """Primer día (≥ `minimo`) en que el p de Welch acumulado baja de 0,05; None si nunca."""
    control, tratamiento = np.asarray(control, dtype=float), np.asarray(tratamiento, dtype=float)
    for d in range(minimo, min(len(control), len(tratamiento)) + 1):
        p = stats.ttest_ind(tratamiento[:d], control[:d], equal_var=False).pvalue
        if p < 0.05:
            return d
    return None


for k in (1, 2, 5, 10, 20):
    print(f"{k:>2} revisiones: {simular_peeking(k):.3f}")
print("OBF (K=5):", round(simular_peeking(5, limites=limites_obf(5, 2.041)), 3))
print("mSPRT:", round(simular_msprt(), 3))

for _, e in experimentos.iterrows():
    x = metricas[(metricas["experiment_id"] == e["experiment_id"]) & (metricas["metric_name"] == e["primary_metric"])]
    x = x.sort_values("date")
    c = x.loc[x["variant"] == "control", "value"].to_numpy()
    t = x.loc[x["variant"] == "tratamiento", "value"].to_numpy()
    print(e["experiment_id"], primer_cruce(c, t))
