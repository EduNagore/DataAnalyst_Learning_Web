import pandas as pd
from datakit.data import load_table

clientes = load_table("customers")
CUASI = ["region", "segment", "acquisition_channel"]  # cuasi-identificadores sin la fecha
NIVELES = ["dia", "mes", "trimestre", "anio"]


def k_anonimato(df: pd.DataFrame, cuasi: list[str]) -> int:
    """El k del conjunto: tamaño del grupo más pequeño de filas con la misma combinación de cuasi-identificadores."""
    return int(df.groupby(cuasi, observed=True).size().min())


def perfil_de_unicidad(df: pd.DataFrame, cuasi: list[str], k: int = 5) -> dict:
    """Devuelve `grupos` (combinaciones distintas), `unicos` (grupos de una sola fila), `k` (el del conjunto) y
    `pct_en_riesgo`: porcentaje de filas que están en grupos de menos de `k` filas."""
    tam = df.groupby(cuasi, observed=True).size()
    return {
        "grupos": int(len(tam)),
        "unicos": int((tam == 1).sum()),
        "k": int(tam.min()),
        "pct_en_riesgo": float(100 * tam[tam < k].sum() / len(df)),
    }


def generalizar_fecha(df: pd.DataFrame, columna: str, nivel: str) -> pd.Series:
    """La fecha reducida al nivel indicado, como texto: «dia» (AAAA-MM-DD), «mes» (AAAA-MM), «trimestre» (AAAA-Tn) o «anio» (AAAA)."""
    f = pd.to_datetime(df[columna])
    if nivel == "dia":
        return f.dt.strftime("%Y-%m-%d")
    if nivel == "mes":
        return f.dt.to_period("M").astype(str)
    if nivel == "trimestre":
        return f.dt.year.astype(str) + "-T" + f.dt.quarter.astype(str)
    if nivel == "anio":
        return f.dt.year.astype(str)
    raise ValueError(f"Nivel desconocido: {nivel}")


def suprimir_raros(df: pd.DataFrame, cuasi: list[str], k: int) -> tuple[pd.DataFrame, float]:
    """Elimina las filas de los grupos con menos de k filas. Devuelve (df resultante, % de filas suprimidas)."""
    tam = df.groupby(cuasi, observed=True)[cuasi[0]].transform("size")
    resultado = df[tam >= k]
    return resultado, float(100 * (len(df) - len(resultado)) / len(df))


def nivel_minimo(df: pd.DataFrame, cuasi: list[str], columna_fecha: str, k: int, max_supresion: float) -> tuple[str, float]:
    """El nivel de generalización de la fecha MÁS FINO (dia < mes < trimestre < anio) con el que, suprimiendo como mucho
    `max_supresion` % de filas, se alcanza k-anonimato. Devuelve (nivel, % suprimido) o lanza ValueError si ninguno basta."""
    for nivel in NIVELES:
        x = df.assign(fecha_g=generalizar_fecha(df, columna_fecha, nivel))
        _, pct = suprimir_raros(x, [*cuasi, "fecha_g"], k)
        if pct <= max_supresion:
            return nivel, pct
    raise ValueError("Ningún nivel alcanza el k pedido con esa supresión máxima.")


for nivel in NIVELES:
    x = clientes.assign(fecha_g=generalizar_fecha(clientes, "signup_date", nivel))
    print(nivel, perfil_de_unicidad(x, [*CUASI, "fecha_g"]))
print(nivel_minimo(clientes, CUASI, "signup_date", k=5, max_supresion=1.0))
