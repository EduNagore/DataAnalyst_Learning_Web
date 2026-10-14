from collections import defaultdict

import numpy as np
import pandas as pd

# Recorridos agregados: canales tocados (en orden), personas que lo recorren y conversiones
recorridos = pd.DataFrame(
    [
        (("paid_social",), 400, 8),
        (("paid_social", "paid_search"), 300, 36),
        (("paid_search",), 500, 40),
        (("email", "paid_search"), 200, 24),
        (("organic", "email"), 150, 18),
        (("organic",), 600, 24),
        (("paid_social", "email", "paid_search"), 100, 22),
        (("direct",), 300, 21),
    ],
    columns=["camino", "personas", "conversiones"],
)


def prob_conversion(rec: pd.DataFrame, quitar: str | None = None) -> float:
    """YA IMPLEMENTADA. Probabilidad de convertir en la cadena de Markov de los recorridos
    (inicio → canales → conversión | abandono). Si `quitar` es un canal, todo el que llega a él abandona."""
    canales = sorted({c for cam in rec["camino"] for c in cam})
    nodos = ["inicio", *canales]
    cuenta: dict = defaultdict(float)
    for cam, personas, conv in zip(rec["camino"], rec["personas"], rec["conversiones"], strict=True):
        pasos = ("inicio", *cam)
        for a, b in zip(pasos[:-1], pasos[1:], strict=True):
            cuenta[(a, b)] += personas
        cuenta[(cam[-1], "conv")] += conv
        cuenta[(cam[-1], "fin")] += personas - conv
    n = len(nodos)
    m, a = np.zeros((n, n)), np.zeros(n)
    salida = np.zeros(n)
    for (de, a_), v in cuenta.items():
        i = nodos.index(de)
        salida[i] += v
        if a_ == "conv":
            a[i] += v
        elif a_ != "fin":
            m[i, nodos.index(a_)] += v
    m, a = m / salida[:, None], a / salida
    if quitar is not None:
        k = nodos.index(quitar)
        m[k, :], a[k] = 0, 0
    return float(np.linalg.solve(np.eye(n) - m, a)[0])


def _repartir(rec: pd.DataFrame, pesos) -> pd.Series:
    credito: dict = defaultdict(float)
    for cam, conv in zip(rec["camino"], rec["conversiones"], strict=True):
        for canal, w in zip(cam, pesos(len(cam)), strict=True):
            credito[canal] += conv * w
    return pd.Series(credito).sort_index()


def credito_ultimo_clic(rec: pd.DataFrame) -> pd.Series:
    """Todo el crédito de cada conversión para el último canal del camino."""
    return _repartir(rec, lambda n: [0.0] * (n - 1) + [1.0])


def credito_primer_clic(rec: pd.DataFrame) -> pd.Series:
    """Todo el crédito para el primer canal."""
    return _repartir(rec, lambda n: [1.0] + [0.0] * (n - 1))


def credito_lineal(rec: pd.DataFrame) -> pd.Series:
    """Crédito repartido a partes iguales entre los toques del camino."""
    return _repartir(rec, lambda n: [1 / n] * n)


def credito_posicion(rec: pd.DataFrame, extremos: float = 0.4) -> pd.Series:
    """En forma de U: `extremos` para el primero y el último; el resto, para los intermedios.
    Con un toque, todo; con dos, mitad y mitad."""

    def pesos(n: int) -> list[float]:
        if n == 1:
            return [1.0]
        if n == 2:
            return [0.5, 0.5]
        return [extremos] + [(1 - 2 * extremos) / (n - 2)] * (n - 2) + [extremos]

    return _repartir(rec, pesos)


def credito_markov(rec: pd.DataFrame) -> pd.Series:
    """Efecto de eliminación de cada canal (1 − P(convertir sin él) / P(convertir)),
    normalizado para que el crédito sume las conversiones totales."""
    base = prob_conversion(rec)
    canales = sorted({c for cam in rec["camino"] for c in cam})
    efecto = pd.Series({c: 1 - prob_conversion(rec, c) / base for c in canales})
    return efecto / efecto.sum() * rec["conversiones"].sum()


tabla = pd.DataFrame(
    {
        "ultimo_clic": credito_ultimo_clic(recorridos),
        "primer_clic": credito_primer_clic(recorridos),
        "lineal": credito_lineal(recorridos),
        "posicion": credito_posicion(recorridos),
        "markov": credito_markov(recorridos),
    }
)
print(tabla.round(1))
print("conversiones totales:", recorridos["conversiones"].sum())
