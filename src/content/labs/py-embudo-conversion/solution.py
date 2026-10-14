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
    s = sessions[["session_id", "app_version", "device", "channel"]].copy()
    s["plataforma"] = np.where(s["app_version"].isna(), "web", "app")
    ev = events[events["event_type"].isin(PASOS)][["session_id", "event_type"]].drop_duplicates().merge(s, on="session_id")
    claves = ["event_type"] if por is None else [por, "event_type"]
    out = ev.groupby(claves).size().rename("sesiones").reset_index().rename(columns={"event_type": "paso"})
    out["paso"] = pd.Categorical(out["paso"], categories=PASOS, ordered=True)
    return out.sort_values(([] if por is None else [por]) + ["paso"], ignore_index=True)


def embudo(events: pd.DataFrame, sessions: pd.DataFrame, por: str | None = None) -> pd.DataFrame:
    """Añade conv_paso (respecto al paso anterior) y conv_total (respecto al primer paso), en %, por grupo."""
    t = sesiones_por_paso(events, sessions, por)
    grupo = t.groupby(por, observed=True) if por else [(None, t)]
    partes = []
    for _, g in grupo:
        g = g.copy()
        g["conv_paso"] = 100 * g["sesiones"] / g["sesiones"].shift(1)
        g["conv_total"] = 100 * g["sesiones"] / g["sesiones"].iloc[0]
        partes.append(g)
    return pd.concat(partes, ignore_index=True)


def comparar_proporciones(x1: int, n1: int, x2: int, n2: int) -> dict:
    """Test z de dos proporciones (varianza agrupada): diferencia (p1 − p2, en puntos porcentuales), z y p bilateral."""
    p1, p2 = x1 / n1, x2 / n2
    pool = (x1 + x2) / (n1 + n2)
    z = (p1 - p2) / np.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    return {"diferencia_pp": float(100 * (p1 - p2)), "z": float(z), "p": float(2 * stats.norm.sf(abs(z)))}


def mayor_fuga(tabla: pd.DataFrame) -> str:
    """Paso con la menor conversión respecto al anterior (excluye el primero)."""
    t = tabla.dropna(subset=["conv_paso"])
    return str(t.loc[t["conv_paso"].idxmin(), "paso"])


tabla = embudo(events, web_sessions)
print(tabla.round(2).to_string(index=False))
print("mayor fuga:", mayor_fuga(tabla))
por_plat = embudo(events, web_sessions, "plataforma")
print(por_plat.round(2).to_string(index=False))
c = por_plat[por_plat["paso"] == "purchase"].set_index("plataforma")["sesiones"]
n = por_plat[por_plat["paso"] == "page_view"].set_index("plataforma")["sesiones"]
print(comparar_proporciones(int(c["web"]), int(n["web"]), int(c["app"]), int(n["app"])))
