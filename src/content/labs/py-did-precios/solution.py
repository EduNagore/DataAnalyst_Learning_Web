import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def serie_mensual(orders, order_items, customers, products) -> pd.DataFrame:
    """Mes → rev_and, rev_resto, q_and, q_resto (Electrónica, sin cancelados)."""
    ped = orders.loc[orders["status"] != "cancelado", ["order_id", "customer_id", "order_date"]]
    x = (
        order_items.merge(ped, on="order_id")
        .merge(customers[["customer_id", "region"]], on="customer_id")
        .merge(products[["product_id", "category_id"]], on="product_id")
    )
    x = x[x["category_id"].str.startswith("cat-00")].copy()
    x["mes"] = x["order_date"].dt.to_period("M").astype(str)
    x["grupo"] = np.where(x["region"].str.startswith("Andaluc"), "and", "resto")
    x["rev"] = x["quantity"] * x["unit_price"]
    g = x.groupby(["mes", "grupo"]).agg(rev=("rev", "sum"), q=("quantity", "sum")).unstack("grupo").fillna(0.0)
    out = pd.DataFrame(
        {
            "rev_and": g[("rev", "and")],
            "rev_resto": g[("rev", "resto")],
            "q_and": g[("q", "and")],
            "q_resto": g[("q", "resto")],
        }
    )
    return out.sort_index()


def _lr(serie, y):
    return np.log(serie[f"{y}_and"] / serie[f"{y}_resto"])


def did_log(serie, y, previo=("2024-03", "2025-02"), posterior=("2025-03", "2026-02")) -> dict:
    """DiD en logaritmos: did, efecto_pct, se, ic_inf, ic_sup (en %)."""
    lr = _lr(serie, y)
    pre, post = lr.loc[previo[0] : previo[1]], lr.loc[posterior[0] : posterior[1]]
    did = float(post.mean() - pre.mean())
    se = float(np.sqrt(pre.var(ddof=1) / len(pre) + post.var(ddof=1) / len(post)))
    gl = len(pre) + len(post) - 2
    t = stats.t.ppf(0.975, gl)
    return {
        "did": did,
        "efecto_pct": float(100 * (np.exp(did) - 1)),
        "se": se,
        "ic_inf": float(100 * (np.exp(did - t * se) - 1)),
        "ic_sup": float(100 * (np.exp(did + t * se) - 1)),
    }


def pendiente_previa(serie, y, previo=("2024-03", "2025-02")) -> tuple[float, float, float]:
    """(pendiente, error estándar, p-valor) de la tendencia previa del log-cociente."""
    pre = _lr(serie, y).loc[previo[0] : previo[1]]
    r = stats.linregress(np.arange(len(pre)), pre.to_numpy())
    return float(r.slope), float(r.stderr), float(r.pvalue)


def estudio_eventos(serie, y, base="2025-02") -> pd.Series:
    """Log-cociente Andalucía / resto menos su valor en el mes base."""
    lr = _lr(serie, y)
    return lr - lr.loc[base]


serie = serie_mensual(orders, order_items, customers, products)
for y in ("rev", "q"):
    print(y, {k: round(v, 4) for k, v in did_log(serie, y).items()})
    print("  tendencia previa:", [round(v, 4) for v in pendiente_previa(serie, y)])
