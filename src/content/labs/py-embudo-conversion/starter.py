import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

events = load_table("events")
web_sessions = load_table("web_sessions")

PASOS = ["page_view", "add_to_cart", "checkout", "purchase"]


def sesiones_por_paso(events: pd.DataFrame, sessions: pd.DataFrame, por: str | None = None) -> pd.DataFrame:
    """Sesiones distintas que alcanzan cada paso. Columnas: paso y sesiones (y la columna `por` si se indica).
    `por` puede ser «plataforma» («web» si no hay app_version, «app» si la hay), «device» o «channel»."""
    # TODO
    ...


def embudo(events: pd.DataFrame, sessions: pd.DataFrame, por: str | None = None) -> pd.DataFrame:
    """Añade conv_paso (respecto al paso anterior) y conv_total (respecto al primer paso), en %, por grupo."""
    # TODO
    ...


def comparar_proporciones(x1: int, n1: int, x2: int, n2: int) -> dict:
    """Test z de dos proporciones (varianza agrupada): diferencia (p1 − p2, en puntos porcentuales), z y p bilateral."""
    # TODO
    ...


def mayor_fuga(tabla: pd.DataFrame) -> str:
    """Paso con la menor conversión respecto al anterior (excluye el primero)."""
    # TODO
    ...


tabla = embudo(events, web_sessions)
print(tabla.round(2).to_string(index=False))
print("mayor fuga:", mayor_fuga(tabla))
por_plat = embudo(events, web_sessions, "plataforma")
print(por_plat.round(2).to_string(index=False))
c = por_plat[por_plat["paso"] == "purchase"].set_index("plataforma")["sesiones"]
n = por_plat[por_plat["paso"] == "page_view"].set_index("plataforma")["sesiones"]
print(comparar_proporciones(int(c["web"]), int(n["web"]), int(c["app"]), int(n["app"])))
