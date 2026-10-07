"""Derivación determinista de generadores aleatorios por tabla.

Cada tabla usa su propio `np.random.Generator`, derivado de la semilla
global y del nombre de la tabla. Así, cambiar el orden en que se generan
las tablas (o generar solo una para depurar) no cambia los números de las
demás: cada una es independiente y reproducible por su propio nombre.
"""

import zlib

import numpy as np


def sub_rng(seed: int, label: str) -> np.random.Generator:
    """Generador hijo determinista: misma (seed, label) -> mismos números."""
    label_hash = zlib.crc32(label.encode("utf-8"))
    return np.random.default_rng([seed, label_hash])
