import pandas as pd
from datakit.data import load_table

clientes = load_table("customers")
CUASI = ["region", "segment", "acquisition_channel"]  # cuasi-identificadores sin la fecha
NIVELES = ["dia", "mes", "trimestre", "anio"]


def k_anonimato(df: pd.DataFrame, cuasi: list[str]) -> int:
    """El k del conjunto: tamaño del grupo más pequeño de filas con la misma combinación de cuasi-identificadores."""
    # TODO
    ...


def perfil_de_unicidad(df: pd.DataFrame, cuasi: list[str], k: int = 5) -> dict:
    """Devuelve `grupos` (combinaciones distintas), `unicos` (grupos de una sola fila), `k` (el del conjunto) y
    `pct_en_riesgo`: porcentaje de filas que están en grupos de menos de `k` filas."""
    # TODO
    ...


def generalizar_fecha(df: pd.DataFrame, columna: str, nivel: str) -> pd.Series:
    """La fecha reducida al nivel indicado, como texto: «dia» (AAAA-MM-DD), «mes» (AAAA-MM), «trimestre» (AAAA-Tn) o «anio» (AAAA)."""
    # TODO
    ...


def suprimir_raros(df: pd.DataFrame, cuasi: list[str], k: int) -> tuple[pd.DataFrame, float]:
    """Elimina las filas de los grupos con menos de k filas. Devuelve (df resultante, % de filas suprimidas)."""
    # TODO
    ...


def nivel_minimo(df: pd.DataFrame, cuasi: list[str], columna_fecha: str, k: int, max_supresion: float) -> tuple[str, float]:
    """El nivel de generalización de la fecha MÁS FINO (dia < mes < trimestre < anio) con el que, suprimiendo como mucho
    `max_supresion` % de filas, se alcanza k-anonimato. Devuelve (nivel, % suprimido) o lanza ValueError si ninguno basta."""
    # TODO
    ...


for nivel in NIVELES:
    x = clientes.assign(fecha_g=generalizar_fecha(clientes, "signup_date", nivel))
    print(nivel, perfil_de_unicidad(x, [*CUASI, "fecha_g"]))
print(nivel_minimo(clientes, CUASI, "signup_date", k=5, max_supresion=1.0))
