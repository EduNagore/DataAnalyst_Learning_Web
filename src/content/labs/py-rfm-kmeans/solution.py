import numpy as np
import pandas as pd
from datakit.data import load_table
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

orders = load_table("orders")
order_items = load_table("order_items")


def calcular_rfm(orders: pd.DataFrame, order_items: pd.DataFrame, fecha: str) -> pd.DataFrame:
    """customer_id, recencia (días), frecuencia (pedidos) y monetario (€) con pedidos no cancelados hasta `fecha`."""
    corte = pd.Timestamp(fecha)
    por_pedido = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    x = orders[(orders["status"] != "cancelado") & (orders["order_date"] <= corte)].copy()
    x["importe"] = x["order_id"].map(por_pedido).fillna(0.0)
    g = x.groupby("customer_id").agg(
        ultima=("order_date", "max"), frecuencia=("order_id", "nunique"), monetario=("importe", "sum")
    )
    g["recencia"] = (corte - g["ultima"]).dt.days
    return g.reset_index()[["customer_id", "recencia", "frecuencia", "monetario"]]


def puntuar_quintiles(rfm: pd.DataFrame) -> pd.DataFrame:
    """Añade R, F, M (1-5, 5 = mejor) con quintiles por rangos (desempate por orden de aparición)."""
    out = rfm.copy()
    etiquetas = [1, 2, 3, 4, 5]
    out["R"] = pd.qcut(out["recencia"].rank(method="first", ascending=False), 5, labels=etiquetas).astype(int)
    out["F"] = pd.qcut(out["frecuencia"].rank(method="first"), 5, labels=etiquetas).astype(int)
    out["M"] = pd.qcut(out["monetario"].rank(method="first"), 5, labels=etiquetas).astype(int)
    return out


def _matriz(rfm: pd.DataFrame) -> np.ndarray:
    Z = np.log1p(rfm[["recencia", "frecuencia", "monetario"]].to_numpy(dtype=float))
    return (Z - Z.mean(axis=0)) / Z.std(axis=0, ddof=1)


def kmeans_rfm(rfm: pd.DataFrame, k: int, seed: int = 0, n_init: int = 10) -> np.ndarray:
    """Etiquetas de k-means sobre log1p(RFM) estandarizado."""
    return KMeans(n_clusters=k, n_init=n_init, random_state=seed).fit(_matriz(rfm)).labels_


def silueta(rfm: pd.DataFrame, etiquetas, muestra: int = 10000) -> float:
    """Silueta media sobre una muestra reproducible de clientes (random_state=0)."""
    return float(silhouette_score(_matriz(rfm), etiquetas, sample_size=muestra, random_state=0))


def perfil_clusters(rfm: pd.DataFrame, etiquetas) -> pd.DataFrame:
    """Por cluster: clientes y medias de recencia, frecuencia y monetario (ordenado por monetario descendente)."""
    d = rfm.assign(cluster=etiquetas)
    p = d.groupby("cluster").agg(
        clientes=("customer_id", "size"),
        recencia=("recencia", "mean"),
        frecuencia=("frecuencia", "mean"),
        monetario=("monetario", "mean"),
    )
    return p.sort_values("monetario", ascending=False)


rfm = calcular_rfm(orders, order_items, "2025-12-31")
puntos = puntuar_quintiles(rfm)
print(len(rfm), "clientes;", int(((puntos.R >= 4) & (puntos.F >= 4) & (puntos.M >= 4)).sum()), "campeones")
for k in (2, 3, 4, 5):
    print(k, round(silueta(rfm, kmeans_rfm(rfm, k)), 3))
etiquetas = kmeans_rfm(rfm, 4)
print(perfil_clusters(rfm, etiquetas).round(1))
otra = kmeans_rfm(rfm, 4, seed=3, n_init=1)
print("estabilidad (ARI):", round(adjusted_rand_score(etiquetas, otra), 3))
