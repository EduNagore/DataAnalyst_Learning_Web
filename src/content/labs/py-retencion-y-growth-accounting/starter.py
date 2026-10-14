import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
customers = load_table("customers")


def actividad_mensual(orders: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cliente y mes con algún pedido no cancelado: customer_id y mes (Period mensual)."""
    # TODO
    ...


def matriz_retencion(actividad: pd.DataFrame) -> pd.DataFrame:
    """Retención por cohorte (mes del primer pedido) y mes k desde el primero: proporción de la cohorte activa."""
    # TODO
    ...


def growth_accounting(actividad: pd.DataFrame) -> pd.DataFrame:
    """Por mes: activos, nuevos, retenidos, resucitados y perdidos."""
    # TODO
    ...


def ratio_rapido(ga: pd.DataFrame) -> pd.Series:
    """(nuevos + resucitados) / perdidos de cada mes."""
    # TODO
    ...


def retencion_por_segmento(actividad: pd.DataFrame, customers: pd.DataFrame, k: int) -> pd.Series:
    """Proporción de cada segmento de cliente que sigue activa k meses después de su primer mes activo."""
    # TODO
    ...


act = actividad_mensual(orders)
ret = matriz_retencion(act)
print(ret.loc["2025-01":"2025-03", [0, 1, 2, 3]].round(3))
ga = growth_accounting(act)
print(ga.tail(4))
print(ratio_rapido(ga).tail(4).round(2).to_dict())
print(retencion_por_segmento(act, customers, 3).round(3).to_dict())
