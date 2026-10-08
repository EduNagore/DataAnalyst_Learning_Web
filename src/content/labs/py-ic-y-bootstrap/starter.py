import numpy as np
from datakit.data import load_table
from scipy import stats

orders = load_table("orders")
items = load_table("order_items")
importe = (items["quantity"] * items["unit_price"]).groupby(items["order_id"]).sum()
orders["importe"] = orders["order_id"].map(importe).fillna(0.0)

muestra = orders.loc[orders["status"] == "completado", "importe"].sample(200, random_state=7).to_numpy()
pedidos500 = orders.sample(500, random_state=7)
cancelados = int((pedidos500["status"] == "cancelado").sum())


def error_estandar(x) -> float:
    """Error estándar de la media: s / sqrt(n), con s muestral (ddof=1)."""
    # TODO
    ...


def ic_media_t(x, nivel: float = 0.95) -> tuple[float, float]:
    """Intervalo t de la media."""
    # TODO
    ...


def ic_bootstrap(x, estadistico=np.mean, nivel: float = 0.95, n_boot: int = 2000, seed: int = 0):
    """Intervalo percentil bootstrap de `estadistico` (reproducible con `seed`)."""
    # TODO
    ...


def ic_wilson(k: int, n: int, nivel: float = 0.95) -> tuple[float, float]:
    """Intervalo de Wilson para la proporción k/n."""
    # TODO
    ...


print("media", round(muestra.mean(), 2), "SE", round(error_estandar(muestra), 2))
print("IC t media", ic_media_t(muestra))
print("IC bootstrap media", ic_bootstrap(muestra))
print("IC bootstrap mediana", ic_bootstrap(muestra, np.median))
print("IC Wilson cancelación", ic_wilson(cancelados, 500))
