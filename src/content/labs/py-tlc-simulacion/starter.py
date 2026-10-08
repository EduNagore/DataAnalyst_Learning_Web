import numpy as np
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")

por_pedido = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
ok = orders[orders["status"] != "cancelado"]
importes = por_pedido.reindex(ok["order_id"]).to_numpy()
print(len(importes), round(importes.mean(), 1), round(importes.std(), 1))


def medias_muestrales(x: np.ndarray, n: int, reps: int, seed: int = 0) -> np.ndarray:
    """`reps` medias de muestras de tamaño `n` (con reemplazo)."""
    # TODO
    ...


def error_estandar_teorico(x: np.ndarray, n: int) -> float:
    """sigma / sqrt(n), con la desviación de la población (ddof=0), 2 decimales."""
    # TODO
    ...


def cobertura_ic(x: np.ndarray, n: int, reps: int = 3000, seed: int = 0) -> float:
    """% de muestras cuyo IC (media ± 1.96·s/√n) contiene la media de x (1 decimal)."""
    # TODO
    ...


for n in (5, 30, 200):
    m = medias_muestrales(importes, n, 5000, seed=1)
    print(n, round(m.mean(), 1), round(m.std(), 1), error_estandar_teorico(importes, n), cobertura_ic(importes, n))
