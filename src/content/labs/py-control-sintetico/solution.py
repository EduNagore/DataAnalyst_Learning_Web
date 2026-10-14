import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy.optimize import nnls

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def panel_regional(orders, order_items, customers, products, desde="2023-01", hasta="2026-02") -> pd.DataFrame:
    """Ingresos mensuales de Electrónica por región (filas = mes, columnas = región); 0 si no hay ventas."""
    ped = orders.loc[orders["status"] != "cancelado", ["order_id", "customer_id", "order_date"]]
    x = (
        order_items.merge(ped, on="order_id")
        .merge(customers[["customer_id", "region"]], on="customer_id")
        .merge(products[["product_id", "category_id"]], on="product_id")
    )
    x = x[x["category_id"].str.startswith("cat-00")].copy()
    x["mes"] = x["order_date"].dt.to_period("M").astype(str)
    x["ingresos"] = x["quantity"] * x["unit_price"]
    panel = x.pivot_table(index="mes", columns="region", values="ingresos", aggfunc="sum", fill_value=0.0)
    return panel.loc[desde:hasta]


def a_indice(panel: pd.DataFrame, fin_previo: str) -> pd.DataFrame:
    """Cada región dividida por su media del periodo previo (hasta `fin_previo`) y multiplicada por 100."""
    return panel / panel.loc[:fin_previo].mean() * 100


def pesos_sinteticos(previo: pd.DataFrame, tratada: str, lam: float = 1000.0) -> pd.Series:
    """Pesos no negativos que suman 1 de las donantes para reproducir la serie previa de `tratada`."""
    donantes = [c for c in previo.columns if c != tratada]
    A = np.vstack([previo[donantes].to_numpy(), lam * np.ones((1, len(donantes)))])
    b = np.concatenate([previo[tratada].to_numpy(), [lam]])
    w, _ = nnls(A, b)
    return pd.Series(w / w.sum(), index=donantes)


def efecto_sintetico(panel: pd.DataFrame, tratada: str, inicio: str = "2025-03") -> dict:
    """pesos, rmse_previo, gap_pct (brecha media posterior en % del sintético) y ratio (RMSPE post/pre)."""
    fin_previo = (pd.Period(inicio, freq="M") - 1).strftime("%Y-%m")
    idx = a_indice(panel, fin_previo)
    w = pesos_sinteticos(idx.loc[:fin_previo], tratada)
    sintetico = idx[w.index] @ w
    brecha = idx[tratada] - sintetico
    previo, posterior = brecha.loc[:fin_previo], brecha.loc[inicio:]
    rmse_pre = float(np.sqrt((previo**2).mean()))
    rmse_post = float(np.sqrt((posterior**2).mean()))
    return {
        "pesos": w,
        "rmse_previo": rmse_pre,
        "gap_pct": float(100 * posterior.mean() / sintetico.loc[inicio:].mean()),
        "ratio": rmse_post / rmse_pre,
    }


def placebos(panel: pd.DataFrame, tratada: str, inicio: str = "2025-03") -> pd.DataFrame:
    """Aplica el método a cada región: region, ratio, gap_pct (ordenado por ratio descendente)."""
    filas = []
    for region in panel.columns:
        r = efecto_sintetico(panel, region, inicio)
        filas.append({"region": region, "ratio": r["ratio"], "gap_pct": r["gap_pct"]})
    return pd.DataFrame(filas).sort_values("ratio", ascending=False, ignore_index=True)


panel = panel_regional(orders, order_items, customers, products)
andalucia = next(c for c in panel.columns if c.startswith("Andaluc"))
r = efecto_sintetico(panel, andalucia)
print(r["pesos"][r["pesos"] > 0.005].round(3).to_string())
print({k: round(v, 3) for k, v in r.items() if k != "pesos"})
pl = placebos(panel, andalucia)
print(pl.head(4).round(2).to_string(index=False))
print("p de permutación:", (pl["ratio"] >= r["ratio"]).mean())
