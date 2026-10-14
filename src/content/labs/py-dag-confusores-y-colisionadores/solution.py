import numpy as np
import pandas as pd

ESCENARIOS = ["confusor", "colisionador", "mediador"]


def simular(escenario: str, n: int = 100000, seed: int = 0) -> pd.DataFrame:
    """Datos simulados del escenario (ver las ecuaciones en las pistas)."""
    if escenario not in ESCENARIOS:
        raise ValueError(f"Escenario desconocido: {escenario!r}")
    rng = np.random.default_rng(seed + ESCENARIOS.index(escenario))
    if escenario == "confusor":
        z = rng.normal(size=n)
        t = (z + rng.normal(size=n) > 0).astype(float)
        y = 2 * t + 3 * z + rng.normal(size=n)
        return pd.DataFrame({"z": z, "t": t, "y": y})
    if escenario == "colisionador":
        t = rng.normal(size=n)
        y = 0.5 * t + rng.normal(size=n)
        c = t + y + rng.normal(size=n)
        return pd.DataFrame({"t": t, "y": y, "c": c})
    t = rng.normal(size=n)
    m = 0.8 * t + rng.normal(size=n)
    y = 0.5 * m + 0.3 * t + rng.normal(size=n)
    return pd.DataFrame({"t": t, "m": m, "y": y})


def efecto_ols(df: pd.DataFrame, controles=()) -> float:
    """Coeficiente de `t` en la regresión de `y` sobre `t` y los controles."""
    columnas = [np.ones(len(df)), df["t"].to_numpy()] + [df[c].to_numpy() for c in controles]
    X = np.column_stack(columnas)
    return float(np.linalg.lstsq(X, df["y"].to_numpy(), rcond=None)[0][1])


def controles_correctos(escenario: str, efecto: str = "total") -> list[str]:
    """Columnas que hay que controlar para estimar el efecto de t sobre y."""
    if escenario == "confusor":
        return ["z"]
    if escenario == "colisionador":
        return []
    if escenario == "mediador":
        return ["m"] if efecto == "directo" else []
    raise ValueError(f"Escenario desconocido: {escenario!r}")


for e in ESCENARIOS:
    df = simular(e)
    print(e, "sin controles:", round(efecto_ols(df), 3), "| con los correctos:", round(efecto_ols(df, controles_correctos(e)), 3))
