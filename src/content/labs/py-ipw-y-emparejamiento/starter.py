import numpy as np
import pandas as pd


def simular_observacional(n: int = 20000, seed: int = 0) -> pd.DataFrame:
    """Dos confusores x1, x2 que afectan al tratamiento t y al resultado y; efecto verdadero de t = 1,0."""
    # TODO
    ...


def propension(df: pd.DataFrame, covariables=("x1", "x2"), iteraciones: int = 25) -> np.ndarray:
    """Probabilidad estimada de tratamiento con una regresión logística (Newton-Raphson)."""
    # TODO
    ...


def diferencia_ingenua(df: pd.DataFrame) -> float:
    """Media de y en tratados menos media en no tratados."""
    # TODO
    ...


def ate_ipw(df: pd.DataFrame, ps: np.ndarray) -> float:
    """Efecto medio con ponderación inversa por la propensión (estimador normalizado)."""
    # TODO
    ...


def att_emparejamiento(df: pd.DataFrame, ps: np.ndarray) -> float:
    """Efecto sobre los tratados: cada tratado se compara con el control de propensión más cercana."""
    # TODO
    ...


def smd(df: pd.DataFrame, columna: str, pesos=None) -> float:
    """Diferencia media estandarizada de `columna` entre tratados y no tratados (con pesos opcionales)."""
    # TODO
    ...


df = simular_observacional()
ps = propension(df)
w = df["t"] / ps + (1 - df["t"]) / (1 - ps)
print("ingenuo:", round(diferencia_ingenua(df), 3), "| IPW:", round(ate_ipw(df, ps), 3), "| emparejamiento:", round(att_emparejamiento(df, ps), 3))
print("SMD x1 antes/después:", round(smd(df, "x1"), 3), round(smd(df, "x1", w), 3))
