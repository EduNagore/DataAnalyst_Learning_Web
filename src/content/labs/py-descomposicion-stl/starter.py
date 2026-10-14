import numpy as np
import pandas as pd
from datakit.data import load_table
from statsmodels.tsa.seasonal import STL

orders = load_table("orders")
calendar = load_table("calendar")


def pedidos_diarios(orders: pd.DataFrame, desde: str = "2024-01-01") -> pd.Series:
    """Pedidos no cancelados por día natural desde `desde`, con frecuencia diaria y 0 en los días sin pedidos."""
    # TODO
    ...


def descomponer(serie: pd.Series, periodo: int = 7, tendencia: int = 61):
    """STL robusto sobre el logaritmo de la serie."""
    # TODO
    ...


def factores_semanales(res) -> pd.Series:
    """Factor multiplicativo de cada día de la semana (0 = lunes) = exp(media de la componente estacional)."""
    # TODO
    ...


def crecimiento_mensual(res) -> float:
    """Crecimiento mensual compuesto de la tendencia (30 días), en fracción."""
    # TODO
    ...


def sigma_robusto(res) -> float:
    """Desviación robusta del residuo: 1,4826 · MAD."""
    # TODO
    ...


def efecto_dias_especiales(res, calendar: pd.DataFrame) -> dict:
    """Efecto medio (%) sobre los pedidos de Black Friday, Navidad y festivos nacionales, a partir del residuo."""
    # TODO
    ...


serie = pedidos_diarios(orders)
res = descomponer(serie)
print(len(serie), "días;", "crecimiento mensual:", round(100 * crecimiento_mensual(res), 1), "%")
print(factores_semanales(res).round(3).to_dict())
print("sigma robusto:", round(sigma_robusto(res), 4))
print({k: round(v, 1) for k, v in efecto_dias_especiales(res, calendar).items()})
