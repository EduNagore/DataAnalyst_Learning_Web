import re
import unicodedata

import numpy as np
import pandas as pd
from datakit.data import load_table
from sklearn.cluster import KMeans

TICKETS = load_table("support_tickets")

PARADAS = {
    "de", "la", "el", "en", "un", "una", "mi", "me", "ha", "he", "no", "y", "que", "por", "al", "del", "los", "las",
    "se", "a", "es", "lo", "con", "para", "mis", "n", "x",
}  # fmt: skip


def normalizar_plantilla(texto: str) -> str:
    """Sustituye cada número por «N» y la categoría citada («categoría Hogar», «categoría Juguetes y bebé»…) por «categoría X»."""
    t = re.sub(r"\d+", "N", texto)
    return re.sub(r"categoría [^ ?.]+( y [^ ?.]+)?", "categoría X", t)


def plantillas(tabla: pd.DataFrame) -> pd.DataFrame:
    """Una fila por plantilla con columnas `plantilla`, `categoria` (la del primer ticket) y `n` (tickets), ordenada por `n` descendente y, a igualdad, por `plantilla`."""
    t = tabla.assign(plantilla=tabla["text"].map(normalizar_plantilla))
    g = t.groupby("plantilla").agg(categoria=("category", "first"), n=("plantilla", "size")).reset_index()
    return g.sort_values(["n", "plantilla"], ascending=[False, True]).reset_index(drop=True)


def tokenizar(texto: str) -> list[str]:
    """Minúsculas, sin acentos, palabras formadas solo por letras a-z, sin las de PARADAS y con al menos 2 letras."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z]+", t) if w not in PARADAS and len(w) > 1]


def tfidf(textos: list[str]):
    """Devuelve (X, vocabulario): X con una fila por texto y una columna por palabra del vocabulario (ordenado alfabéticamente),
    con valor = recuentos × idf, donde idf = ln((1 + n) / (1 + df)) + 1, y cada fila normalizada a longitud 1 (norma L2)."""
    docs = [tokenizar(t) for t in textos]
    vocab = sorted({w for d in docs for w in d})
    ix = {w: i for i, w in enumerate(vocab)}
    X = np.zeros((len(docs), len(vocab)))
    for i, d in enumerate(docs):
        for w in d:
            X[i, ix[w]] += 1
    df = (X > 0).sum(axis=0)
    X = X * (np.log((1 + len(docs)) / (1 + df)) + 1)
    norma = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norma == 0, 1, norma), vocab


def similitud(X: np.ndarray) -> np.ndarray:
    """Matriz de similitud del coseno entre todas las filas (con filas ya normalizadas es un producto de matrices)."""
    return X @ X.T


def vecinos(S: np.ndarray, i: int, k: int) -> list[int]:
    """Índices de los k textos más parecidos al i (sin incluirlo), de más a menos parecido y, a igualdad, por índice."""
    orden = sorted((j for j in range(len(S)) if j != i), key=lambda j: (-round(S[i, j], 12), j))
    return orden[:k]


def pares_parecidos(S: np.ndarray, umbral: float) -> list[tuple]:
    """Pares (i, j, similitud) con i < j y similitud >= umbral, de mayor a menor similitud."""
    n = len(S)
    pares = [(i, j, float(S[i, j])) for i in range(n) for j in range(i + 1, n) if S[i, j] >= umbral]
    return sorted(pares, key=lambda p: (-p[2], p[0], p[1]))


def agrupar(X: np.ndarray, k: int, semilla: int = 0) -> np.ndarray:
    """YA IMPLEMENTADA. K-means con 10 inicializaciones; devuelve el grupo de cada fila."""
    return KMeans(n_clusters=k, n_init=10, random_state=semilla).fit_predict(X)


def pureza(grupos, categorias) -> float:
    """Para cada grupo, el número de plantillas de su categoría más frecuente; se suma y se divide entre el total de plantillas."""
    tabla = pd.crosstab(np.asarray(grupos), np.asarray(categorias))
    return float(tabla.max(axis=1).sum() / tabla.values.sum())


def rango_pureza(X, categorias, k: int, semillas) -> tuple:
    """(mínimo, máximo) de la pureza al agrupar con `k` grupos con cada una de las semillas."""
    ps = [pureza(agrupar(X, k, s), categorias) for s in semillas]
    return min(ps), max(ps)


if __name__ == "__main__":
    pl = plantillas(TICKETS)
    X, vocab = tfidf(list(pl["plantilla"]))
    S = similitud(X)
    print(len(pl), "plantillas;", len(vocab), "palabras")
    for i, j, s in pares_parecidos(S, 0.5):
        print(round(s, 2), pl.loc[i, "plantilla"], "|", pl.loc[j, "plantilla"], pl.loc[i, "categoria"], pl.loc[j, "categoria"])
    for k in (5, 8, 12):
        print(k, rango_pureza(X, pl["categoria"], k, range(6)))
