import numpy as np
import pandas as pd
from datakit.data import load_table
from datakit.lumen import panel_bajas
from scipy import stats

panel = panel_bajas(load_table("subscriptions"), load_table("shipments"), load_table("orders"))
panel["anual"] = (panel["plan"] == "anual").astype(int)


def ajustar_logit(df: pd.DataFrame, y: str, x: list[str], iteraciones: int = 50) -> dict:
    """Regresión logística (Newton-Raphson). Devuelve `params` y `se` (Series con índice `const` + `x`)."""
    # TODO
    ...


def razones_de_odds(df: pd.DataFrame, y: str, x: list[str]) -> pd.DataFrame:
    """Tabla con `odds_ratio`, `ic_inf` e `ic_sup` (95 %) de cada variable (sin la constante)."""
    # TODO
    ...


def probabilidades(df: pd.DataFrame, params: pd.Series) -> np.ndarray:
    """Probabilidad predicha para cada fila con los coeficientes ajustados."""
    # TODO
    ...


def auc(y, p) -> float:
    """Área bajo la curva ROC: probabilidad de que un positivo reciba mayor puntuación que un negativo."""
    # TODO
    ...


x = ["expuesto", "anual", "mrr_eur", "k"]
print(razones_de_odds(panel, "cancela", x).round(3))
modelo = ajustar_logit(panel, "cancela", x)
print("AUC (en muestra):", round(auc(panel["cancela"], probabilidades(panel, modelo["params"])), 3))
print(panel.groupby("expuesto")["cancela"].mean().round(4).to_dict())
