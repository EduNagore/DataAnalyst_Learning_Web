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
    r, al, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = res["x"].to_numpy(), res["tx"].to_numpy(), res["T"].to_numpy()
    a1 = gammaln(r + x) - gammaln(r) + r * np.log(al)
    a2 = gammaln(a + b) + gammaln(b + x) - gammaln(b) - gammaln(a + b + x)
    a3 = -(r + x) * np.log(al + T)
    a4 = np.log(a) - np.log(b + np.maximum(x, 1) - 1) - (r + x) * np.log(al + tx)
    return a1 + a2 + np.logaddexp(a3, np.where(x > 0, a4, -np.inf))


def ajustar_bgnbd(res: pd.DataFrame) -> dict:
    """Maximiza la verosimilitud (en logaritmos de los parámetros, para mantenerlos positivos)."""

    def nll(p):
        r, al, a, b = np.exp(p)
        return -loglik_bgnbd({"r": r, "alpha": al, "a": a, "b": b}, res).sum()

    s = minimize(nll, np.log([1.0, 10.0, 1.0, 1.0]), method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-4, "maxiter": 2000})
    r, al, a, b = np.exp(s.x)
    return {"r": float(r), "alpha": float(al), "a": float(a), "b": float(b)}


def compras_esperadas(res: pd.DataFrame, params: dict, semanas: float) -> np.ndarray:
    """Compras repetidas esperadas de cada cliente en las próximas `semanas`, dado su historial."""
    r, al, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = res["x"].to_numpy(), res["tx"].to_numpy(), res["T"].to_numpy()
    t = semanas
    num = (a + b + x - 1) / (a - 1) * (1 - ((al + T) / (al + T + t)) ** (r + x) * hyp2f1(r + x, b + x, a + b + x - 1, t / (al + T + t)))
    den = 1 + (x > 0) * a / np.maximum(b + x - 1, 1e-9) * ((al + T) / (al + tx)) ** (r + x)
    return num / den


def ajustar_gamma_gamma(res: pd.DataFrame) -> dict:
    """Modelo Gamma-Gamma del valor por compra (p, q, gamma), con el valor medio m y el número de compras n."""
    n, m = res["n"].to_numpy(), res["m"].to_numpy()

    def nll(p):
        pp, q, g = np.exp(p)
        ll = (
            gammaln(pp * n + q) - gammaln(pp * n) - gammaln(q) + q * np.log(g)
            + (pp * n - 1) * np.log(m) + pp * n * np.log(n) - (pp * n + q) * np.log(g + m * n)
        )
        return -ll.sum()

    s = minimize(nll, np.log([2.0, 2.0, 10.0]), method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-4, "maxiter": 2000})
    p, q, g = np.exp(s.x)
    return {"p": float(p), "q": float(q), "gamma": float(g)}


def valor_esperado(res: pd.DataFrame, gg: dict) -> np.ndarray:
    """Valor medio esperado por compra de cada cliente: p · (γ + m·n) / (p·n + q − 1)."""
    n, m = res["n"].to_numpy(), res["m"].to_numpy()
    return gg["p"] * (gg["gamma"] + m * n) / (gg["p"] * n + gg["q"] - 1)


def clv(res: pd.DataFrame, bg: dict, gg: dict, semanas: float) -> np.ndarray:
    """Ingresos esperados de cada cliente en las próximas `semanas`: compras esperadas × valor esperado."""
    return compras_esperadas(res, bg, semanas) * valor_esperado(res, gg)


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
