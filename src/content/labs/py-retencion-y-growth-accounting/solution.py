import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
customers = load_table("customers")


def actividad_mensual(orders: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cliente y mes con algún pedido no cancelado: customer_id y mes (Period mensual)."""
    x = orders.loc[orders["status"] != "cancelado", ["customer_id", "order_date"]].copy()
    x["mes"] = pd.to_datetime(x["order_date"]).dt.to_period("M")
    return x[["customer_id", "mes"]].drop_duplicates().reset_index(drop=True)


def _con_cohorte(actividad: pd.DataFrame) -> pd.DataFrame:
    a = actividad.copy()
    a["cohorte"] = a.groupby("customer_id")["mes"].transform("min")
    a["k"] = (a["mes"] - a["cohorte"]).apply(lambda d: d.n)
    return a


def matriz_retencion(actividad: pd.DataFrame) -> pd.DataFrame:
    """Retención por cohorte (mes del primer pedido) y mes k desde el primero: proporción de la cohorte activa."""
    a = _con_cohorte(actividad)
    t = a.groupby(["cohorte", "k"])["customer_id"].nunique().unstack()
    return t.div(t[0], axis=0)


def growth_accounting(actividad: pd.DataFrame) -> pd.DataFrame:
    """Por mes: activos, nuevos (primer mes activo), retenidos (activos también el mes anterior),
    resucitados (activos tras estar inactivos) y perdidos (activos el mes anterior y no este)."""
    meses = sorted(actividad["mes"].unique())
    por_mes = {m: set(g["customer_id"]) for m, g in actividad.groupby("mes")}
    vistos: set = set()
    filas = []
    for i, m in enumerate(meses):
        actual = por_mes[m]
        previo = por_mes[meses[i - 1]] if i > 0 and meses[i - 1] == m - 1 else set()
        filas.append(
            {
                "mes": m,
                "activos": len(actual),
                "nuevos": len(actual - vistos),
                "retenidos": len(actual & previo),
                "resucitados": len((actual - previo) & vistos),
                "perdidos": len(previo - actual),
            }
        )
        vistos |= actual
    return pd.DataFrame(filas).set_index("mes")


def ratio_rapido(ga: pd.DataFrame) -> pd.Series:
    """(nuevos + resucitados) / perdidos de cada mes."""
    return (ga["nuevos"] + ga["resucitados"]) / ga["perdidos"].where(ga["perdidos"] > 0)


def retencion_por_segmento(actividad: pd.DataFrame, customers: pd.DataFrame, k: int) -> pd.Series:
    """Proporción de cada segmento de cliente que sigue activa k meses después de su primer mes activo."""
    a = _con_cohorte(actividad).merge(customers[["customer_id", "segment"]], on="customer_id")
    base = a[a["k"] == 0].groupby("segment")["customer_id"].nunique()
    activos = a[a["k"] == k].groupby("segment")["customer_id"].nunique()
    return (activos / base).reindex(base.index)


act = actividad_mensual(orders)
ret = matriz_retencion(act)
print(ret.loc["2025-01":"2025-03", [0, 1, 2, 3]].round(3))
ga = growth_accounting(act)
print(ga.tail(4))
print(ratio_rapido(ga).tail(4).round(2).to_dict())
print(retencion_por_segmento(act, customers, 3).round(3).to_dict())
