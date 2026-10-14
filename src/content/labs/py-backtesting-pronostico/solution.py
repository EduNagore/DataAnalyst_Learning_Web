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
    ultimo = train.to_numpy()[-m:]
    return np.array([ultimo[i % m] for i in range(h)])


def pronostico_snaive_deriva(train: pd.Series, h: int, m: int = 7, k: int = 28) -> np.ndarray:
    """Naive estacional con crecimiento: el último ciclo multiplicado por el crecimiento diario medio
    observado entre la última semana y la semana de hace `k` días."""
    v = train.to_numpy()
    reciente, anterior = v[-m:].mean(), v[-m - k : -k].mean()
    g = (reciente / anterior) ** (1 / k)
    return pronostico_snaive(train, h, m) * g ** (np.arange(h) + 1)


def pronostico_holt_winters(train: pd.Series, h: int) -> np.ndarray:
    """Holt-Winters aditivo con tendencia amortiguada y estacionalidad semanal, sobre el logaritmo."""
    modelo = ExponentialSmoothing(
        np.log(train.to_numpy()), trend="add", damped_trend=True, seasonal="add", seasonal_periods=7
    ).fit(optimized=True)
    return np.exp(modelo.forecast(h))


def metricas(real, pred, escala: float) -> dict:
    """mae, rmse, mape (%), mase (mae / escala) y sesgo_pct (suma de pronósticos / suma real − 1, en %)."""
    real, pred = np.asarray(real, dtype=float), np.asarray(pred, dtype=float)
    error = real - pred
    mae = float(np.mean(np.abs(error)))
    return {
        "mae": mae,
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mape": float(100 * np.mean(np.abs(error / real))),
        "mase": mae / escala,
        "sesgo_pct": float(100 * (pred.sum() / real.sum() - 1)),
    }


def backtest(serie: pd.Series, metodo, h: int = 28, inicio: str = "2025-01-01", paso: int = 28) -> pd.DataFrame:
    """Origen móvil: para cada origen entrena con todo lo anterior y pronostica `h` días; una fila por origen."""
    filas = []
    for origen in pd.date_range(inicio, serie.index[-1], freq=f"{paso}D"):
        test = serie.loc[origen : origen + pd.Timedelta(days=h - 1)]
        if len(test) < h:
            break
        train = serie.loc[: origen - pd.Timedelta(days=1)]
        v = train.to_numpy()
        escala = float(np.mean(np.abs(v[7:] - v[:-7])))
        fila = metricas(test.to_numpy(), metodo(train, h), escala)
        fila["origen"] = origen
        filas.append(fila)
    return pd.DataFrame(filas).set_index("origen")


serie = pedidos_diarios(orders)
metodos = {"naive estacional": pronostico_snaive, "naive + crecimiento": pronostico_snaive_deriva, "Holt-Winters": pronostico_holt_winters}
resumen = pd.DataFrame({nombre: backtest(serie, f).mean() for nombre, f in metodos.items()}).T
print(resumen.round(3))
