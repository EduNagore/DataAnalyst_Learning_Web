import pandas as pd
from datakit.data import load_table
from datakit.llm import MockLLM

pedidos = load_table("orders")


def tokens(texto: str) -> int:
    """Tokens aproximados de un texto (≈ 4 caracteres por token): usa MockLLM.count_tokens."""
    # TODO
    ...


def coste_eur(tokens_entrada: int, tokens_salida: int, precio_entrada_1m: float, precio_salida_1m: float) -> float:
    """Coste en euros de una llamada, con precios (de ejemplo) por millón de tokens de entrada y de salida."""
    # TODO
    ...


def filas_que_caben(df: pd.DataFrame, presupuesto: int) -> int:
    """Cuántas filas del DataFrame, escritas como CSV (cabecera incluida), caben en `presupuesto` tokens contando la
    cabecera y todas las filas anteriores. Devuelve 0 si ni siquiera cabe la cabecera."""
    # TODO
    ...


def resumen_para_prompt(df: pd.DataFrame, max_valores: int = 5) -> str:
    """Resumen compacto de un DataFrame para pegar en un prompt, una línea por columna:
    «nombre (tipo) | nulos=N | distintos=N | ejemplos o rango». Las columnas numéricas o de fecha dan «min…max»;
    las demás, sus `max_valores` valores más frecuentes separados por «; ». Las columnas identificadoras (`id` o
    `*_id`) NO muestran ejemplos: ponen «identificador (sin ejemplos)». Primera línea: «filas=N»."""
    # TODO
    ...


def muestra_estratificada(df: pd.DataFrame, por: str, n: int, semilla: int = 0) -> pd.DataFrame:
    """Muestra de unas `n` filas que conserva la proporción de cada valor de `por` (al menos una fila por valor),
    reproducible con la semilla. Ordenada por el índice original."""
    # TODO
    ...


muestra = pedidos.head(10_000)
estimado = tokens(muestra.to_csv(index=False)) * len(pedidos) / len(muestra)
print("CSV completo (estimado con 10.000 filas):", round(estimado), "tokens | resumen:", tokens(resumen_para_prompt(pedidos)), "tokens")
print("filas que caben en 8.000 tokens:", filas_que_caben(pedidos, 8000))
print("coste ilustrativo del CSV completo:", round(coste_eur(round(estimado), 500, 3.0, 15.0), 2), "€")
