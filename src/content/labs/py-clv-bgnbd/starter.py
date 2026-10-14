import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy.optimize import minimize
from scipy.special import gammaln, hyp2f1

orders = load_table("orders")
order_items = load_table("order_items")
CORTE = pd.Timestamp("2024-12-31")


def resumen_clientes(orders: pd.DataFrame, order_items: pd.DataFrame, corte: pd.Timestamp) -> pd.DataFrame:
    """YA IMPLEMENTADA. Una fila por cliente con compras hasta `corte` (pedidos no cancelados, un «día de compra»
    por fecha): x = compras repetidas, tx = semanas entre la primera y la última, T = semanas entre la primera
    y el corte, n = días de compra y m = valor medio por día de compra."""
    o = orders[orders["status"] != "cancelado"].copy()
    o["dia"] = pd.to_datetime(o["order_date"]).dt.normalize()
    valor = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    o["valor"] = o["order_id"].map(valor)
    dias = o.groupby(["customer_id", "dia"], as_index=False)["valor"].sum()
    dias = dias[dias["dia"] <= corte]
    g = dias.groupby("customer_id").agg(primero=("dia", "min"), ultimo=("dia", "max"), n=("dia", "size"), m=("valor", "mean"))
    return pd.DataFrame(
        {
            "x": (g["n"] - 1).astype(float),
            "tx": (g["ultimo"] - g["primero"]).dt.days / 7,
            "T": (corte - g["primero"]).dt.days / 7,
            "n": g["n"].astype(float),
            "m": g["m"],
        }
    )


def loglik_bgnbd(params: dict, res: pd.DataFrame) -> np.ndarray:
    """Log-verosimilitud de cada cliente en el BG/NBD (r, alpha, a, b)."""
    # TODO
    ...


def ajustar_bgnbd(res: pd.DataFrame) -> dict:
    """Maximiza la verosimilitud (en logaritmos de los parámetros, para mantenerlos positivos)."""
    # TODO
    ...


def compras_esperadas(res: pd.DataFrame, params: dict, semanas: float) -> np.ndarray:
    """Compras repetidas esperadas de cada cliente en las próximas `semanas`, dado su historial."""
    # TODO
    ...


def ajustar_gamma_gamma(res: pd.DataFrame) -> dict:
    """Modelo Gamma-Gamma del valor por compra (p, q, gamma), con el valor medio m y el número de compras n."""
    # TODO
    ...


def valor_esperado(res: pd.DataFrame, gg: dict) -> np.ndarray:
    """Valor medio esperado por compra de cada cliente: p · (γ + m·n) / (p·n + q − 1)."""
    # TODO
    ...


def clv(res: pd.DataFrame, bg: dict, gg: dict, semanas: float) -> np.ndarray:
    """Ingresos esperados de cada cliente en las próximas `semanas`: compras esperadas × valor esperado."""
    # TODO
    ...


res = resumen_clientes(orders, order_items, CORTE)
bg = ajustar_bgnbd(res)
gg = ajustar_gamma_gamma(res)
print({k: round(v, 3) for k, v in bg.items()}, {k: round(v, 2) for k, v in gg.items()})

# Validación: 52 semanas posteriores al corte
o = orders[orders["status"] != "cancelado"].copy()
o["dia"] = pd.to_datetime(o["order_date"]).dt.normalize()
real = o[(o["dia"] > CORTE) & (o["dia"] <= CORTE + pd.Timedelta(days=364))].groupby("customer_id")["dia"].nunique()
real = res.index.map(real).fillna(0).to_numpy()
pred = compras_esperadas(res, bg, 52)
print("compras 2025: previstas", round(pred.sum()), "reales", int(real.sum()))
print("ingresos 2025 previstos (M€):", round(clv(res, bg, gg, 52).sum() / 1e6, 2))
