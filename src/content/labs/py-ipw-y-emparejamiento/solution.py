import numpy as np
import pandas as pd


def simular_observacional(n: int = 20000, seed: int = 0) -> pd.DataFrame:
    """Dos confusores x1, x2 que afectan al tratamiento t y al resultado y; efecto verdadero de t = 1,0."""
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    p = 1 / (1 + np.exp(-(0.8 * x1 - 0.6 * x2)))
    t = (rng.random(n) < p).astype(int)
    y = 1.0 * t + 2 * x1 - 1.5 * x2 + rng.normal(size=n)
    return pd.DataFrame({"x1": x1, "x2": x2, "t": t, "y": y})


def propension(df: pd.DataFrame, covariables=("x1", "x2"), iteraciones: int = 25) -> np.ndarray:
    """Probabilidad estimada de tratamiento con una regresión logística (Newton-Raphson)."""
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy() for c in covariables])
    t = df["t"].to_numpy(dtype=float)
    beta = np.zeros(X.shape[1])
    for _ in range(iteraciones):
        p = 1 / (1 + np.exp(-X @ beta))
        W = p * (1 - p)
        paso = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (t - p))
        beta = beta + paso
        if np.max(np.abs(paso)) < 1e-10:
            break
    return 1 / (1 + np.exp(-X @ beta))


def diferencia_ingenua(df: pd.DataFrame) -> float:
    """Media de y en tratados menos media en no tratados."""
    return float(df.loc[df["t"] == 1, "y"].mean() - df.loc[df["t"] == 0, "y"].mean())


def ate_ipw(df: pd.DataFrame, ps: np.ndarray) -> float:
    """Efecto medio con ponderación inversa por la propensión (estimador normalizado)."""
    t, y = df["t"].to_numpy(), df["y"].to_numpy()
    w = t / ps + (1 - t) / (1 - ps)
    return float(np.sum(w * t * y) / np.sum(w * t) - np.sum(w * (1 - t) * y) / np.sum(w * (1 - t)))


def att_emparejamiento(df: pd.DataFrame, ps: np.ndarray) -> float:
    """Efecto sobre los tratados: cada tratado se compara con el control de propensión más cercana."""
    t, y = df["t"].to_numpy(), df["y"].to_numpy()
    tratados, controles = np.where(t == 1)[0], np.where(t == 0)[0]
    orden = controles[np.argsort(ps[controles])]
    ps_ord = ps[orden]
    pos = np.searchsorted(ps_ord, ps[tratados])
    izq = np.clip(pos - 1, 0, len(orden) - 1)
    der = np.clip(pos, 0, len(orden) - 1)
    elegir_der = np.abs(ps_ord[der] - ps[tratados]) < np.abs(ps[tratados] - ps_ord[izq])
    vecino = np.where(elegir_der, orden[der], orden[izq])
    return float(np.mean(y[tratados] - y[vecino]))


def smd(df: pd.DataFrame, columna: str, pesos=None) -> float:
    """Diferencia media estandarizada de `columna` entre tratados y no tratados (con pesos opcionales)."""
    x, t = df[columna].to_numpy(), df["t"].to_numpy()
    w = np.ones(len(x)) if pesos is None else np.asarray(pesos)
    m1 = np.average(x[t == 1], weights=w[t == 1])
    m0 = np.average(x[t == 0], weights=w[t == 0])
    return float((m1 - m0) / np.sqrt((x[t == 1].var() + x[t == 0].var()) / 2))


df = simular_observacional()
ps = propension(df)
w = df["t"] / ps + (1 - df["t"]) / (1 - ps)
print("ingenuo:", round(diferencia_ingenua(df), 3), "| IPW:", round(ate_ipw(df, ps), 3), "| emparejamiento:", round(att_emparejamiento(df, ps), 3))
print("SMD x1 antes/después:", round(smd(df, "x1"), 3), round(smd(df, "x1", w), 3))
