import numpy as np
import pandas as pd
from datakit.data import load_table
from statsmodels.tsa.seasonal import STL

orders = load_table("orders")
calendar = load_table("calendar")


def pedidos_diarios(orders: pd.DataFrame, desde: str = "2024-01-01") -> pd.Series:
    """Pedidos no cancelados por día natural desde `desde`, con frecuencia diaria y 0 en los días sin pedidos."""
    x = orders.loc[orders["status"] != "cancelado"]
    serie = x.groupby(pd.to_datetime(x["order_date"])).size().asfreq("D", fill_value=0)
    return serie.loc[desde:].astype(float)


def descomponer(serie: pd.Series, periodo: int = 7, tendencia: int = 61):
    """STL robusto sobre el logaritmo de la serie."""
    return STL(np.log(serie), period=periodo, trend=tendencia, robust=True).fit()


def factores_semanales(res) -> pd.Series:
    """Factor multiplicativo de cada día de la semana (0 = lunes) = exp(media de la componente estacional)."""
    estacional = res.seasonal
    return np.exp(estacional.groupby(estacional.index.dayofweek).mean())


def crecimiento_mensual(res) -> float:
    """Crecimiento mensual compuesto de la tendencia (30 días), en fracción."""
    t = res.trend
    dias = (t.index[-1] - t.index[0]).days
    return float(np.exp(t.iloc[-1] - t.iloc[0]) ** (30 / dias) - 1)


def sigma_robusto(res) -> float:
    """Desviación robusta del residuo: 1,4826 · MAD."""
    r = res.resid
    return float(1.4826 * np.median(np.abs(r - np.median(r))))


def efecto_dias_especiales(res, calendar: pd.DataFrame) -> dict:
    """Efecto medio (%) sobre los pedidos de Black Friday, Navidad y festivos nacionales, a partir del residuo."""
    cal = calendar.assign(date=pd.to_datetime(calendar["date"])).set_index("date").reindex(res.resid.index)
    r = res.resid

    def efecto(mascara) -> float:
        return float(100 * (np.exp(r[mascara.fillna(False).to_numpy(dtype=bool)].mean()) - 1))

    return {
        "black_friday": efecto(cal["sale_event_name"] == "Black Friday"),
        "navidad": efecto(cal["sale_event_name"] == "Navidad"),
        "festivo_nacional": efecto(cal["is_holiday_national"]),
    }


serie = pedidos_diarios(orders)
res = descomponer(serie)
print(len(serie), "días;", "crecimiento mensual:", round(100 * crecimiento_mensual(res), 1), "%")
print(factores_semanales(res).round(3).to_dict())
print("sigma robusto:", round(sigma_robusto(res), 4))
print({k: round(v, 1) for k, v in efecto_dias_especiales(res, calendar).items()})
