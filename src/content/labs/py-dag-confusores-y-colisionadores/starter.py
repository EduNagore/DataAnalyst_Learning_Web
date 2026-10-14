import numpy as np
import pandas as pd

ESCENARIOS = ["confusor", "colisionador", "mediador"]


def simular(escenario: str, n: int = 100000, seed: int = 0) -> pd.DataFrame:
    """Datos simulados del escenario (ver las ecuaciones en las pistas)."""
    # TODO
    ...


def efecto_ols(df: pd.DataFrame, controles=()) -> float:
    """Coeficiente de `t` en la regresión de `y` sobre `t` y los controles."""
    # TODO
    ...


def controles_correctos(escenario: str, efecto: str = "total") -> list[str]:
    """Columnas que hay que controlar para estimar el efecto de t sobre y."""
    # TODO
    ...


for e in ESCENARIOS:
    df = simular(e)
    print(e, "sin controles:", round(efecto_ols(df), 3), "| con los correctos:", round(efecto_ols(df, controles_correctos(e)), 3))
