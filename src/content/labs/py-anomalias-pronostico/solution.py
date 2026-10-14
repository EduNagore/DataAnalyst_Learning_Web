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
    por_pedido = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    x = orders.loc[orders["status"] != "cancelado", ["order_id", "order_date"]].copy()
    x["importe"] = x["order_id"].map(por_pedido).fillna(0.0)
    serie = x.groupby(pd.to_datetime(x["order_date"]))["importe"].sum().asfreq("D", fill_value=0.0)
    return serie.loc[desde:]


def pronostico_hw(train: pd.Series, h: int) -> np.ndarray:
    """Holt-Winters aditivo amortiguado con estacionalidad semanal sobre el logaritmo."""
    modelo = ExponentialSmoothing(
        np.log(train.to_numpy()), trend="add", damped_trend=True, seasonal="add", seasonal_periods=7
    ).fit(optimized=True)
    return np.exp(modelo.forecast(h))


def errores_log(serie: pd.Series, inicio: str = "2025-01-01", h: int = 28, paso: int = 28) -> pd.Series:
    """Errores logarítmicos log(real / pronóstico) de todos los orígenes móviles con horizonte completo."""
    partes = []
    for origen in pd.date_range(inicio, serie.index[-1], freq=f"{paso}D"):
        test = serie.loc[origen : origen + pd.Timedelta(days=h - 1)]
        if len(test) < h:
            break
        pred = pronostico_hw(serie.loc[: origen - pd.Timedelta(days=1)], h)
        partes.append(pd.Series(np.log(test.to_numpy() / pred), index=test.index))
    return pd.concat(partes)


def parametros_robustos(errores: pd.Series) -> tuple[float, float]:
    """(mediana, sigma robusto = 1,4826 · MAD) de los errores."""
    med = float(np.median(errores))
    return med, float(1.4826 * np.median(np.abs(errores - med)))


def puntuaciones_z(errores: pd.Series, mediana: float, sigma: float) -> pd.Series:
    """z robusto de cada error."""
    return (errores - mediana) / sigma


def rachas_anomalas(z: pd.Series, umbral: float = 3.0, minimo: int = 3) -> pd.DataFrame:
    """Rachas de días consecutivos con |z| > umbral y el mismo signo: inicio, fin, dias, direccion y z_medio."""
    signo = np.sign(z.where(z.abs() > umbral, 0.0))
    filas, inicio, previo, n, ultimo = [], None, 0.0, 0, None
    for fecha, s in signo.items():
        if s != 0 and s == previo:
            n += 1
        else:
            if previo != 0 and n >= minimo:
                filas.append((inicio, ultimo, n, previo))
            inicio, n = (fecha, 1) if s != 0 else (None, 0)
        previo, ultimo = s, fecha
    if previo != 0 and n >= minimo:
        filas.append((inicio, ultimo, n, previo))
    out = pd.DataFrame(filas, columns=["inicio", "fin", "dias", "signo"])
    out["direccion"] = np.where(out["signo"] < 0, "baja", "sube")
    out["z_medio"] = [float(z.loc[r.inicio : r.fin].mean()) for r in out.itertuples()]
    return out[["inicio", "fin", "dias", "direccion", "z_medio"]]


serie = ingresos_diarios(orders, order_items)
e = errores_log(serie)
mediana, sigma = parametros_robustos(e.loc[:"2026-02-28"])
z = puntuaciones_z(e, mediana, sigma)
print(len(e), round(mediana, 4), round(sigma, 4))
print(rachas_anomalas(z).round(1).to_string(index=False))
