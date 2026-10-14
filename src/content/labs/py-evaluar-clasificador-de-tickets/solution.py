import re

import numpy as np
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
    m = pd.DataFrame(0, index=list(clases), columns=list(clases), dtype=int)
    for real, pred in zip(y_true, y_pred, strict=True):
        m.loc[real, pred] += 1
    return m


def metricas_por_clase(m: pd.DataFrame) -> pd.DataFrame:
    """Por clase: precision, exhaustividad, f1 y soporte (nº de casos reales). Si el denominador es 0, la métrica vale 0."""
    vp = pd.Series(np.diag(m.values), index=m.index, dtype=float)
    pred = m.sum(axis=0).astype(float)
    real = m.sum(axis=1).astype(float)
    prec = (vp / pred.where(pred > 0)).fillna(0.0)
    rec = (vp / real.where(real > 0)).fillna(0.0)
    f1 = (2 * prec * rec / (prec + rec).where((prec + rec) > 0)).fillna(0.0)
    return pd.DataFrame({"precision": prec, "exhaustividad": rec, "f1": f1, "soporte": real.astype(int)})


def exactitud(m: pd.DataFrame) -> float:
    """Aciertos / total."""
    return float(np.trace(m.values) / m.values.sum())


def f1_macro(met: pd.DataFrame) -> float:
    """Media simple de la F1 de todas las clases."""
    return float(met["f1"].mean())


def kappa_cohen(m: pd.DataFrame) -> float:
    """κ = (po − pe) / (1 − pe) con po = exactitud y pe = Σ (marginal fila × marginal columna) / total²."""
    total = m.values.sum()
    po = np.trace(m.values) / total
    pe = float((m.sum(axis=1).values * m.sum(axis=0).values).sum() / total**2)
    return float((po - pe) / (1 - pe))


def errores_frecuentes(m: pd.DataFrame, k: int = 3) -> list[tuple]:
    """Los k errores más frecuentes como (real, predicha, n), de mayor a menor n y, a igualdad, por orden alfabético de (real, predicha)."""
    filas = [(r, p, int(m.loc[r, p])) for r in m.index for p in m.columns if r != p and m.loc[r, p] > 0]
    filas.sort(key=lambda x: (-x[2], x[0], x[1]))
    return filas[:k]


if __name__ == "__main__":
    pred = [clasificar_por_reglas(t) for t in ETIQUETADOS["text"]]
    m = matriz_confusion(ETIQUETADOS["label"], pred, CLASES)
    met = metricas_por_clase(m)
    print(m)
    print(met.round(3))
    print(round(exactitud(m), 3), round(f1_macro(met), 3), round(kappa_cohen(m), 3))
    print(errores_frecuentes(m))
