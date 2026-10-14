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
    # TODO
    ...


def auc_logistico(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]) -> float:
    """AUC en prueba de una regresión logística entrenada con `cols` (variables estandarizadas con el entrenamiento)."""
    # TODO
    ...


def auc_boosting(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], seed: int = 0) -> float:
    """AUC en prueba de un HistGradientBoostingClassifier."""
    # TODO
    ...


def importancia_permutacion(modelo, X: pd.DataFrame, y, n_rep: int = 5, seed: int = 0) -> pd.Series:
    """Caída media del AUC al barajar cada columna de X (modelo con predict_proba)."""
    # TODO
    ...


train, test = dividir_temporal(panel, "2025-07-01")
print(len(train), len(test), round(train["cancela"].mean(), 4), round(test["cancela"].mean(), 4))
print("logística (expuesto):", round(auc_logistico(train, test, ["expuesto"]), 3))
cols = ["expuesto", "anual", "mrr_eur", "k"]
print("boosting:", round(auc_boosting(train, test, cols), 3))
print("con fuga (activa_hoy):", round(auc_logistico(train, test, ["expuesto", "activa_hoy"]), 3))
gb = HistGradientBoostingClassifier(random_state=0).fit(train[cols], train["cancela"])
print(importancia_permutacion(gb, test[cols], test["cancela"]).round(4))
