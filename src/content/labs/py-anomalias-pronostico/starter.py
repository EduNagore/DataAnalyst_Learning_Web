import warnings

import numpy as np
import pandas as pd
from datakit.data import load_table
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")

orders = load_table("orders")
order_items = load_table("order_items")


def ingresos_diarios(orders: pd.DataFrame, order_items: pd.DataFrame, desde: str = "2024-01-01") -> pd.Series:
    """Ingresos (quantity × unit_price) de los pedidos no cancelados por día natural, con 0 en los días vacíos."""
    # TODO
    ...


def pronostico_hw(train: pd.Series, h: int) -> np.ndarray:
    """Holt-Winters aditivo amortiguado con estacionalidad semanal sobre el logaritmo."""
    # TODO
    ...


def errores_log(serie: pd.Series, inicio: str = "2025-01-01", h: int = 28, paso: int = 28) -> pd.Series:
    """Errores logarítmicos log(real / pronóstico) de todos los orígenes móviles con horizonte completo."""
    # TODO
    ...


def parametros_robustos(errores: pd.Series) -> tuple[float, float]:
    """(mediana, sigma robusto = 1,4826 · MAD) de los errores."""
    # TODO
    ...


def puntuaciones_z(errores: pd.Series, mediana: float, sigma: float) -> pd.Series:
    """z robusto de cada error."""
    # TODO
    ...


def rachas_anomalas(z: pd.Series, umbral: float = 3.0, minimo: int = 3) -> pd.DataFrame:
    """Rachas de días consecutivos con |z| > umbral y el mismo signo: inicio, fin, dias, direccion y z_medio."""
    # TODO
    ...


serie = ingresos_diarios(orders, order_items)
e = errores_log(serie)
mediana, sigma = parametros_robustos(e.loc[:"2026-02-28"])
z = puntuaciones_z(e, mediana, sigma)
print(len(e), round(mediana, 4), round(sigma, 4))
print(rachas_anomalas(z).round(1).to_string(index=False))
