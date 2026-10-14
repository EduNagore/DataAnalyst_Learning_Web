import numpy as np
import pandas as pd
from datakit.data import load_table

clientes = load_table("customers")
por_region = clientes.groupby("region").size()
por_celda = clientes.groupby(["region", "segment", "acquisition_channel"]).size()


def ruido_laplace(epsilon: float, rng: np.random.Generator, tamano=None, sensibilidad: float = 1.0):
    """Ruido de Laplace con escala sensibilidad / epsilon (media 0)."""
    # TODO
    ...


def conteos_privados(conteos: pd.Series, epsilon: float, semilla: int = 0) -> pd.Series:
    """Mecanismo de Laplace sobre un histograma: suma a cada conteo un ruido de escala 1/epsilon (un cliente cambia
    como mucho un conteo en 1) y recorta los negativos a 0 (post-procesado, no gasta privacidad). Mantiene el índice."""
    # TODO
    ...


def error_absoluto_medio(conteos: pd.Series, epsilon: float, repeticiones: int = 2000, semilla: int = 0) -> float:
    """Error absoluto medio por celda al repetir el mecanismo `repeticiones` veces (sin recortar a 0)."""
    # TODO
    ...


def epsilon_para_error(error_objetivo: float, sensibilidad: float = 1.0) -> float:
    """El epsilon con el que el error absoluto esperado del mecanismo de Laplace es `error_objetivo`
    (el error absoluto medio de Laplace(b) es b = sensibilidad / epsilon)."""
    # TODO
    ...


def presupuesto_total(epsilons: list[float]) -> float:
    """Composición secuencial básica: el epsilon total gastado por varias consultas sobre los mismos datos es la suma."""
    # TODO
    ...


def error_relativo_medio(conteos: pd.Series, epsilon: float, repeticiones: int = 2000, semilla: int = 0) -> float:
    """Error relativo medio (|ruido| / conteo) en % sobre todas las celdas y repeticiones."""
    # TODO
    ...


for eps in (0.1, 1.0):
    print(
        "epsilon", eps,
        "| región:", round(error_relativo_medio(por_region, eps), 3), "%",
        "| celdas región×segmento×canal:", round(error_relativo_medio(por_celda, eps), 3), "%",
    )
print(conteos_privados(por_region, 1.0).round(0).head(3).to_dict())
