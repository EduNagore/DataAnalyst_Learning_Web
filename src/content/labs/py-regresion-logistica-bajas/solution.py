import numpy as np
import pandas as pd
from datakit.data import load_table
from datakit.lumen import panel_bajas
from scipy import stats

panel = panel_bajas(load_table("subscriptions"), load_table("shipments"), load_table("orders"))
panel["anual"] = (panel["plan"] == "anual").astype(int)


def ajustar_logit(df: pd.DataFrame, y: str, x: list[str], iteraciones: int = 50) -> dict:
    """Regresión logística (Newton-Raphson). Devuelve `params` y `se` (Series con índice `const` + `x`)."""
    nombres = ["const"] + list(x)
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(dtype=float) for c in x])
    yv = df[y].to_numpy(dtype=float)
    beta = np.zeros(X.shape[1])
    for _ in range(iteraciones):
        p = 1 / (1 + np.exp(-X @ beta))
        W = p * (1 - p)
        paso = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (yv - p))
        beta = beta + paso
        if np.max(np.abs(paso)) < 1e-10:
            break
    p = 1 / (1 + np.exp(-X @ beta))
    cov = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))
    return {"params": pd.Series(beta, index=nombres), "se": pd.Series(np.sqrt(np.diag(cov)), index=nombres)}


def razones_de_odds(df: pd.DataFrame, y: str, x: list[str]) -> pd.DataFrame:
    """Tabla con `odds_ratio`, `ic_inf` e `ic_sup` (95 %) de cada variable (sin la constante)."""
    r = ajustar_logit(df, y, x)
    z = stats.norm.ppf(0.975)
    b, se = r["params"].drop("const"), r["se"].drop("const")
    return pd.DataFrame({"odds_ratio": np.exp(b), "ic_inf": np.exp(b - z * se), "ic_sup": np.exp(b + z * se)})


def probabilidades(df: pd.DataFrame, params: pd.Series) -> np.ndarray:
    """Probabilidad predicha para cada fila con los coeficientes ajustados."""
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(dtype=float) for c in params.index[1:]])
    return 1 / (1 + np.exp(-X @ params.to_numpy()))


def auc(y, p) -> float:
    """Área bajo la curva ROC: probabilidad de que un positivo reciba mayor puntuación que un negativo."""
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    rangos = stats.rankdata(p)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    return float((rangos[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


x = ["expuesto", "anual", "mrr_eur", "k"]
print(razones_de_odds(panel, "cancela", x).round(3))
modelo = ajustar_logit(panel, "cancela", x)
print("AUC (en muestra):", round(auc(panel["cancela"], probabilidades(panel, modelo["params"])), 3))
print(panel.groupby("expuesto")["cancela"].mean().round(4).to_dict())
