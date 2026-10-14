import numpy as np
import pandas as pd
from datakit.data import load_table
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

orders = load_table("orders")
order_items = load_table("order_items")


def calcular_rfm(orders: pd.DataFrame, order_items: pd.DataFrame, fecha: str) -> pd.DataFrame:
    """customer_id, recencia (días), frecuencia (pedidos) y monetario (€) con pedidos no cancelados hasta `fecha`."""
    # TODO
    ...


def puntuar_quintiles(rfm: pd.DataFrame) -> pd.DataFrame:
    """Añade R, F, M (1-5, 5 = mejor) con quintiles por rangos (desempate por orden de aparición)."""
    # TODO
    ...


def kmeans_rfm(rfm: pd.DataFrame, k: int, seed: int = 0, n_init: int = 10) -> np.ndarray:
    """Etiquetas de k-means sobre log1p(RFM) estandarizado."""
    # TODO
    ...


def silueta(rfm: pd.DataFrame, etiquetas, muestra: int = 10000) -> float:
    """Silueta media sobre una muestra reproducible de clientes (random_state=0)."""
    # TODO
    ...


def perfil_clusters(rfm: pd.DataFrame, etiquetas) -> pd.DataFrame:
    """Por cluster: clientes y medias de recencia, frecuencia y monetario (ordenado por monetario descendente)."""
    # TODO
    ...


rfm = calcular_rfm(orders, order_items, "2025-12-31")
puntos = puntuar_quintiles(rfm)
print(len(rfm), "clientes;", int(((puntos.R >= 4) & (puntos.F >= 4) & (puntos.M >= 4)).sum()), "campeones")
for k in (2, 3, 4, 5):
    print(k, round(silueta(rfm, kmeans_rfm(rfm, k)), 3))
etiquetas = kmeans_rfm(rfm, 4)
print(perfil_clusters(rfm, etiquetas).round(1))
otra = kmeans_rfm(rfm, 4, seed=3, n_init=1)
print("estabilidad (ARI):", round(adjusted_rand_score(etiquetas, otra), 3))
