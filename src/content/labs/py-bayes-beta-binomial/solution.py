import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

order_items = load_table("order_items")
returns = load_table("returns")


def posterior_beta(k: int, n: int, a: float = 1.0, b: float = 1.0) -> tuple[float, float]:
    """Parámetros del posterior Beta(a + k, b + n - k)."""
    return a + k, b + n - k


def resumen_posterior(a: float, b: float, nivel: float = 0.95) -> dict:
    """media, mediana, inferior, superior y p_mayor_que(umbral) del posterior Beta(a, b)."""
    dist = stats.beta(a, b)
    lo, hi = dist.ppf([(1 - nivel) / 2, (1 + nivel) / 2])
    return {
        "media": float(dist.mean()),
        "mediana": float(dist.median()),
        "inferior": float(lo),
        "superior": float(hi),
        "p_mayor_que": lambda umbral: float(dist.sf(umbral)),
    }


def prob_mayor(a1: float, b1: float, a2: float, b2: float, n_sim: int = 200000, seed: int = 0) -> float:
    """P(theta2 > theta1) por simulación de los dos posteriores."""
    rng = np.random.default_rng(seed)
    x1 = rng.beta(a1, b1, n_sim)
    x2 = rng.beta(a2, b2, n_sim)
    return float(np.mean(x2 > x1))


def ranking_encogido(order_items: pd.DataFrame, returns: pd.DataFrame, fuerza: float = 400) -> pd.DataFrame:
    """product_id, k, n, tasa, tasa_bayes (ordenado por tasa_bayes descendente)."""
    devuelto = order_items["order_item_id"].isin(returns["order_item_id"])
    g = devuelto.groupby(order_items["product_id"]).agg(k="sum", n="size").reset_index()
    g["tasa"] = g["k"] / g["n"]
    media = g["k"].sum() / g["n"].sum()
    a, b = media * fuerza, (1 - media) * fuerza
    g["tasa_bayes"] = (a + g["k"]) / (a + b + g["n"])
    return g.sort_values("tasa_bayes", ascending=False, ignore_index=True)


a, b = posterior_beta(57, 510)
print("prior plano:", {k: v for k, v in resumen_posterior(a, b).items() if k != "p_mayor_que"})
a, b = posterior_beta(57, 510, 28.07, 371.93)
print("prior informado:", {k: v for k, v in resumen_posterior(a, b).items() if k != "p_mayor_que"})
print(ranking_encogido(order_items, returns).head(5).round(4))
