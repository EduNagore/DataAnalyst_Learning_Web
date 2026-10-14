import pandas as pd
from datakit.data import load_table

events = load_table("events")
web_sessions = load_table("web_sessions")
orders = load_table("orders")


def sesiones_con_duplicados(events: pd.DataFrame, tipo: str = "purchase") -> pd.DataFrame:
    """Sesiones con más de un evento de `tipo`: session_id, n_eventos y app_version."""
    # TODO
    ...


def deduplicar(events: pd.DataFrame) -> pd.DataFrame:
    """Conserva el primer evento de cada (sesión, tipo, propiedades) y elimina los repetidos."""
    # TODO
    ...


def compras_por_version(events: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    """Por versión de la app («web» si no hay): sesiones, eventos_compra, sesiones_con_compra, por_100_eventos,
    por_100_sesiones y sobreestimacion_pct (eventos / sesiones con compra − 1, en %)."""
    # TODO
    ...


def cobertura_frente_a_pedidos(events: pd.DataFrame, orders: pd.DataFrame) -> float:
    """Eventos de compra únicos (tras deduplicar) entre pedidos no cancelados, en %."""
    # TODO
    ...


d = sesiones_con_duplicados(events)
print(len(d), d["app_version"].value_counts().to_dict())
r = compras_por_version(events, web_sessions)
print(r.round(3))
print(len(events), "→", len(deduplicar(events)))
print("cobertura frente a pedidos:", round(cobertura_frente_a_pedidos(events, orders), 2), "%")
