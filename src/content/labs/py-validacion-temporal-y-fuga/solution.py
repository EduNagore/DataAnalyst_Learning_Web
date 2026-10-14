import numpy as np
import pandas as pd
from datakit.data import load_table
from datakit.lumen import panel_bajas
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

panel = panel_bajas(load_table("subscriptions"), load_table("shipments"), load_table("orders"))
panel["anual"] = (panel["plan"] == "anual").astype(int)
# Variable «de otra tabla»: estado actual de la suscripción (¿es información disponible al predecir?)
panel["activa_hoy"] = panel["cancelled_at"].isna().astype(int)


def dividir_temporal(panel: pd.DataFrame, corte: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Entrenamiento (t < corte) y prueba (t >= corte)."""
    c = pd.Timestamp(corte)
    return panel[panel["t"] < c].copy(), panel[panel["t"] >= c].copy()


def auc_logistico(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]) -> float:
    """AUC en prueba de una regresión logística entrenada con `cols` (variables estandarizadas con el entrenamiento)."""
    media, desv = train[cols].mean(), train[cols].std().replace(0, 1)
    modelo = LogisticRegression(max_iter=1000).fit((train[cols] - media) / desv, train["cancela"])
    p = modelo.predict_proba((test[cols] - media) / desv)[:, 1]
    return float(roc_auc_score(test["cancela"], p))


def auc_boosting(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], seed: int = 0) -> float:
    """AUC en prueba de un HistGradientBoostingClassifier."""
    modelo = HistGradientBoostingClassifier(random_state=seed).fit(train[cols], train["cancela"])
    return float(roc_auc_score(test["cancela"], modelo.predict_proba(test[cols])[:, 1]))


def importancia_permutacion(modelo, X: pd.DataFrame, y, n_rep: int = 5, seed: int = 0) -> pd.Series:
    """Caída media del AUC al barajar cada columna de X (modelo con predict_proba)."""
    rng = np.random.default_rng(seed)
    base = roc_auc_score(y, modelo.predict_proba(X)[:, 1])
    out = {}
    for c in X.columns:
        caidas = []
        for _ in range(n_rep):
            Xp = X.copy()
            Xp[c] = rng.permutation(Xp[c].to_numpy())
            caidas.append(base - roc_auc_score(y, modelo.predict_proba(Xp)[:, 1]))
        out[c] = float(np.mean(caidas))
    return pd.Series(out).sort_values(ascending=False)


train, test = dividir_temporal(panel, "2025-07-01")
print(len(train), len(test), round(train["cancela"].mean(), 4), round(test["cancela"].mean(), 4))
print("logística (expuesto):", round(auc_logistico(train, test, ["expuesto"]), 3))
cols = ["expuesto", "anual", "mrr_eur", "k"]
print("boosting:", round(auc_boosting(train, test, cols), 3))
print("con fuga (activa_hoy):", round(auc_logistico(train, test, ["expuesto", "activa_hoy"]), 3))
gb = HistGradientBoostingClassifier(random_state=0).fit(train[cols], train["cancela"])
print(importancia_permutacion(gb, test[cols], test["cancela"]).round(4))
