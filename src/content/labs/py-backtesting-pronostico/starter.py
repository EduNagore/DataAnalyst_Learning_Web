import warnings

import numpy as np
import pandas as pd
from datakit.data import load_table
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")

orders = load_table("orders")


def pedidos_diarios(orders: pd.DataFrame, desde: str = "2024-01-01") -> pd.Series:
    """Pedidos no cancelados por día natural desde `desde` (frecuencia diaria, 0 si no hay pedidos)."""
    x = orders.loc[orders["status"] != "cancelado"]
    serie = x.groupby(pd.to_datetime(x["order_date"])).size().asfreq("D", fill_value=0)
    return serie.loc[desde:].astype(float)


def pronostico_snaive(train: pd.Series, h: int, m: int = 7) -> np.ndarray:
    """Naive estacional: repite el último ciclo de `m` días."""
    # TODO
    ...


def pronostico_snaive_deriva(train: pd.Series, h: int, m: int = 7, k: int = 28) -> np.ndarray:
    """Naive estacional con crecimiento: el último ciclo multiplicado por el crecimiento diario medio
    observado entre la última semana y la semana de hace `k` días."""
    # TODO
    ...


def pronostico_holt_winters(train: pd.Series, h: int) -> np.ndarray:
    """Holt-Winters aditivo con tendencia amortiguada y estacionalidad semanal, sobre el logaritmo."""
    # TODO
    ...


def metricas(real, pred, escala: float) -> dict:
    """mae, rmse, mape (%), mase (mae / escala) y sesgo_pct (suma de pronósticos / suma real − 1, en %)."""
    # TODO
    ...


def backtest(serie: pd.Series, metodo, h: int = 28, inicio: str = "2025-01-01", paso: int = 28) -> pd.DataFrame:
    """Origen móvil: para cada origen entrena con todo lo anterior y pronostica `h` días; una fila por origen."""
    # TODO
    ...


serie = pedidos_diarios(orders)
metodos = {
    "naive estacional": pronostico_snaive,
    "naive + crecimiento": pronostico_snaive_deriva,
    "Holt-Winters": pronostico_holt_winters,
}
resumen = pd.DataFrame({nombre: backtest(serie, f).mean() for nombre, f in metodos.items()}).T
print(resumen.round(3))
