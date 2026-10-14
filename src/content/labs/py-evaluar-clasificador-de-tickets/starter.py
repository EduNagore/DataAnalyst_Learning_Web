import re

import numpy as np  # noqa: F401
import pandas as pd
from datakit.data import load_table

CLASES = ["app", "devoluciones", "envio", "pagos", "producto"]

_t = load_table("support_tickets")
ETIQUETADOS = _t[_t["label"].notna()][["ticket_id", "text", "label"]].reset_index(drop=True)

REGLAS = [
    ("app", r"\bapp\b|aplicación"),
    ("pagos", r"cobrad|tarjeta|factura|cupón|pag|importe|descuento"),
    ("devoluciones", r"devol|reembolso"),
    ("envio", r"envío|paquete|pedido lleva|transportista|almacén|entrega"),
]


def clasificar_por_reglas(texto: str) -> str:
    """YA IMPLEMENTADA. Primera regla que encaja (en orden); si ninguna, «producto»."""
    t = texto.lower()
    for clase, patron in REGLAS:
        if re.search(patron, t):
            return clase
    return "producto"


def matriz_confusion(y_true, y_pred, clases) -> pd.DataFrame:
    """Matriz de confusión como DataFrame de enteros: filas = etiqueta real, columnas = predicha, ambas en el orden de `clases`."""
    # TODO
    ...


def metricas_por_clase(m: pd.DataFrame) -> pd.DataFrame:
    """Por clase: precision, exhaustividad, f1 y soporte (nº de casos reales). Si el denominador es 0, la métrica vale 0."""
    # TODO
    ...


def exactitud(m: pd.DataFrame) -> float:
    """Aciertos / total."""
    # TODO
    ...


def f1_macro(met: pd.DataFrame) -> float:
    """Media simple de la F1 de todas las clases."""
    # TODO
    ...


def kappa_cohen(m: pd.DataFrame) -> float:
    """κ = (po − pe) / (1 − pe) con po = exactitud y pe = Σ (marginal fila × marginal columna) / total²."""
    # TODO
    ...


def errores_frecuentes(m: pd.DataFrame, k: int = 3) -> list[tuple]:
    """Los k errores más frecuentes como (real, predicha, n), de mayor a menor n y, a igualdad, por orden alfabético de (real, predicha)."""
    # TODO
    ...


if __name__ == "__main__":
    pred = [clasificar_por_reglas(t) for t in ETIQUETADOS["text"]]
    m = matriz_confusion(ETIQUETADOS["label"], pred, CLASES)
    met = metricas_por_clase(m)
    print(m)
    print(met.round(3))
    print(round(exactitud(m), 3), round(f1_macro(met), 3), round(kappa_cohen(m), 3))
    print(errores_frecuentes(m))
