from itertools import product

import numpy as np
import pandas as pd

CANALES = ["busqueda", "redes"]
DECAY_REAL = {"busqueda": 0.3, "redes": 0.6}
K_REAL = {"busqueda": 1.0, "redes": 2.0}
BETA_REAL = {"busqueda": 3000.0, "redes": 4500.0}


def _adstock_ref(x, decay):
    out, previo = np.zeros(len(x)), 0.0
    for i, v in enumerate(x):
        previo = v + decay * previo
        out[i] = previo
    return out


def simular_semanas(semilla: int = 7, n: int = 156) -> pd.DataFrame:
    """YA IMPLEMENTADA. 156 semanas de inversión (en miles de €) en dos canales y de ventas (en €) con efecto
    conocido: base + tendencia + estacionalidad + canales con arrastre (adstock) y saturación + ruido."""
    rng = np.random.default_rng(semilla)
    t = np.arange(n)
    gasto = {
        c: np.clip(rng.gamma(2, 0.45, n) * (1 + 0.3 * np.sin(2 * np.pi * (t + 8 * i) / 52)), 0.05, None)
        for i, c in enumerate(CANALES)
    }
    ventas = 20000 + 15 * t + 1500 * np.sin(2 * np.pi * t / 52) + rng.normal(0, 250, n)
    for c in CANALES:
        x = _adstock_ref(gasto[c], DECAY_REAL[c]) * (1 - DECAY_REAL[c])
        ventas = ventas + BETA_REAL[c] * (1 - np.exp(-x / K_REAL[c]))
    return pd.DataFrame({"semana": t, **{f"gasto_{c}": gasto[c] for c in CANALES}, "ventas": ventas})


def roas_verdadero(df: pd.DataFrame) -> dict:
    """YA IMPLEMENTADA. ROAS medio real de la simulación (solo se puede saber porque los datos son sintéticos)."""
    out = {}
    for c in CANALES:
        x = _adstock_ref(df[f"gasto_{c}"].to_numpy(float), DECAY_REAL[c]) * (1 - DECAY_REAL[c])
        out[c] = float(BETA_REAL[c] * (1 - np.exp(-x / K_REAL[c])).sum() / (1000 * df[f"gasto_{c}"].sum()))
    return out


def adstock(x: np.ndarray, decay: float) -> np.ndarray:
    """Arrastre geométrico: a[t] = x[t] + decay · a[t−1]."""
    out = np.zeros(len(x))
    previo = 0.0
    for i, v in enumerate(x):
        previo = v + decay * previo
        out[i] = previo
    return out


def saturacion(x: np.ndarray, k: float) -> np.ndarray:
    """Rendimientos decrecientes: 1 − exp(−x / k)."""
    return 1 - np.exp(-np.asarray(x) / k)


def ajustar(df: pd.DataFrame, decays=(0.0, 0.15, 0.3, 0.45, 0.6, 0.75), ks=(0.5, 1.0, 2.0, 4.0)) -> dict:
    """Busca en rejilla (decay, k) de cada canal y, para cada combinación, estima por mínimos cuadrados
    ventas ~ constante + tendencia + seno + coseno anuales + Σ βc · saturación(adstock(gasto_c))
    (el adstock se normaliza dividiendo por 1/(1−decay)). Devuelve la mejor: decay, k, beta (por canal) y r2."""
    t = df["semana"].to_numpy(float)
    base = np.column_stack([np.ones(len(df)), t, np.sin(2 * np.pi * t / 52), np.cos(2 * np.pi * t / 52)])
    y = df["ventas"].to_numpy(float)
    mejor = None
    opciones = list(product(decays, ks))
    for combo in product(opciones, repeat=len(CANALES)):
        cols = []
        for c, (d, k) in zip(CANALES, combo, strict=True):
            cols.append(saturacion(adstock(df[f"gasto_{c}"].to_numpy(float), d) * (1 - d), k))
        X = np.column_stack([base, *cols])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = float(((y - X @ coef) ** 2).sum())
        if mejor is None or sse < mejor[0]:
            mejor = (sse, combo, coef)
    sse, combo, coef = mejor
    return {
        "decay": {c: combo[i][0] for i, c in enumerate(CANALES)},
        "k": {c: combo[i][1] for i, c in enumerate(CANALES)},
        "beta": {c: float(coef[4 + i]) for i, c in enumerate(CANALES)},
        "r2": 1 - sse / float(((y - y.mean()) ** 2).sum()),
    }


def roas_medio(df: pd.DataFrame, ajuste: dict) -> dict:
    """Ventas atribuibles a cada canal (β · saturación(adstock)) por euro invertido (el gasto está en miles de €)."""
    out = {}
    for c in CANALES:
        x = adstock(df[f"gasto_{c}"].to_numpy(float), ajuste["decay"][c]) * (1 - ajuste["decay"][c])
        out[c] = float(ajuste["beta"][c] * saturacion(x, ajuste["k"][c]).sum() / (1000 * df[f"gasto_{c}"].sum()))
    return out


df = simular_semanas()
aj = ajustar(df)
print("decay estimado:", aj["decay"], "| k estimado:", aj["k"])
print("R²:", round(aj["r2"], 3))
print("ROAS medio estimado:", {c: round(v, 2) for c, v in roas_medio(df, aj).items()})
print("ROAS medio verdadero:", {c: round(v, 2) for c, v in roas_verdadero(df).items()})
