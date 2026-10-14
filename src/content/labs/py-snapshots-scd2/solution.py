import pandas as pd
from datakit.data import load_table

base = load_table("customers").sort_values("customer_id").head(2000).reset_index(drop=True)[
    ["customer_id", "region", "segment"]
]


def extracto(dia: str, cambios: dict | None = None, quitar: tuple = ()) -> pd.DataFrame:
    """YA IMPLEMENTADA. La tabla de clientes tal y como la ve la fuente un día: aplica `cambios`
    ({customer_id: nuevo segmento}), elimina los clientes de `quitar` y sella `updated_at` con el día del
    cambio (el resto conserva 2026-01-01)."""
    e = base.assign(updated_at=pd.Timestamp("2026-01-01"))
    for cid, seg in (cambios or {}).items():
        e.loc[e["customer_id"] == cid, ["segment", "updated_at"]] = [seg, pd.Timestamp(dia)]
    return e[~e["customer_id"].isin(quitar)].reset_index(drop=True)


def snapshot(historial, actual, clave, ahora, estrategia="timestamp", updated_at="updated_at", check_cols=(), hard_deletes="ignore"):
    """Aplica una ejecución de `dbt snapshot` y devuelve el historial actualizado (tipo 2: SCD2).
    El historial tiene las columnas de la fuente más `dbt_valid_from` y `dbt_valid_to` (nulo = fila vigente).
    - Claves nuevas: se insertan con dbt_valid_from = su `updated_at` (estrategia timestamp) o `ahora` (check).
    - Cambio detectado: con timestamp, `updated_at` de la fuente es posterior al de la fila vigente; con check,
      alguna de `check_cols` difiere. Se cierra la fila vigente (dbt_valid_to = dbt_valid_from de la nueva) y se
      inserta la versión nueva.
    - Claves que desaparecen de la fuente: con hard_deletes="invalidate" se cierra la fila vigente en `ahora`;
      con "ignore", no se toca."""
    ahora = pd.Timestamp(ahora)
    h = historial.copy()
    vigente = h[h["dbt_valid_to"].isna()].set_index(clave)
    act = actual.set_index(clave)
    nuevos = act.loc[~act.index.isin(vigente.index)]
    comunes = act.loc[act.index.isin(vigente.index)]
    previo = vigente.loc[comunes.index]
    if estrategia == "timestamp":
        cambiado = comunes[updated_at] > previo[updated_at]
    else:
        cambiado = (comunes[list(check_cols)].astype(str) != previo[list(check_cols)].astype(str)).any(axis=1)
    versiones = pd.concat([nuevos, comunes[cambiado]])
    if estrategia == "timestamp":
        versiones = versiones.assign(dbt_valid_from=versiones[updated_at])
    else:
        versiones = versiones.assign(dbt_valid_from=ahora)
    versiones = versiones.assign(dbt_valid_to=pd.NaT).reset_index()
    cerrar = comunes[cambiado].index
    if hard_deletes == "invalidate":
        desaparecidas = vigente.index.difference(act.index)
        h.loc[h[clave].isin(desaparecidas) & h["dbt_valid_to"].isna(), "dbt_valid_to"] = ahora
    if len(cerrar):
        nuevo_inicio = versiones.set_index(clave).loc[cerrar, "dbt_valid_from"]
        for k in cerrar:
            h.loc[(h[clave] == k) & h["dbt_valid_to"].isna(), "dbt_valid_to"] = nuevo_inicio[k]
    salida = pd.concat([h, versiones[h.columns.tolist()]], ignore_index=True)
    for c in ("dbt_valid_from", "dbt_valid_to"):
        salida[c] = pd.to_datetime(salida[c])
    return salida


def vigentes(snap: pd.DataFrame) -> pd.DataFrame:
    """Las filas con dbt_valid_to nulo (la versión actual de cada clave)."""
    return snap[snap["dbt_valid_to"].isna()].reset_index(drop=True)


def en_fecha(snap: pd.DataFrame, fecha: str) -> pd.DataFrame:
    """La tabla tal y como era en `fecha`: filas con dbt_valid_from <= fecha y (dbt_valid_to nulo o > fecha)."""
    f = pd.Timestamp(fecha)
    return snap[(snap["dbt_valid_from"] <= f) & (snap["dbt_valid_to"].isna() | (snap["dbt_valid_to"] > f))].reset_index(drop=True)


vacio = extracto("2026-01-01").iloc[0:0].assign(dbt_valid_from=pd.NaT, dbt_valid_to=pd.NaT)
ids = base["customer_id"].tolist()
s1 = snapshot(vacio, extracto("2026-01-01"), "customer_id", "2026-01-01")
s2 = snapshot(s1, extracto("2026-02-01", {ids[0]: "vip", ids[1]: "vip"}), "customer_id", "2026-02-01")
s3 = snapshot(s2, extracto("2026-03-01", {ids[0]: "habitual"}, quitar=(ids[5],)), "customer_id", "2026-03-01", hard_deletes="invalidate")
print(len(s1), len(s2), len(s3), "| vigentes:", len(vigentes(s3)), "| en febrero:", len(en_fecha(s3, "2026-02-15")))
