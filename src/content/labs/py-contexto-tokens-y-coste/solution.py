import pandas as pd
from datakit.data import load_table
from datakit.llm import MockLLM

pedidos = load_table("orders")


def tokens(texto: str) -> int:
    """Tokens aproximados de un texto (≈ 4 caracteres por token): usa MockLLM.count_tokens."""
    return MockLLM.count_tokens(texto)


def coste_eur(tokens_entrada: int, tokens_salida: int, precio_entrada_1m: float, precio_salida_1m: float) -> float:
    """Coste en euros de una llamada, con precios (de ejemplo) por millón de tokens de entrada y de salida."""
    return tokens_entrada / 1e6 * precio_entrada_1m + tokens_salida / 1e6 * precio_salida_1m


def filas_que_caben(df: pd.DataFrame, presupuesto: int) -> int:
    """Cuántas filas del DataFrame, escritas como CSV (cabecera incluida), caben en `presupuesto` tokens contando la
    cabecera y todas las filas anteriores. Devuelve 0 si ni siquiera cabe la cabecera."""
    cabecera = tokens(",".join(df.columns) + "\n")
    if cabecera > presupuesto:
        return 0
    usado, n = cabecera, 0
    # cada línea cuesta al menos 1 token: nunca caben más filas que tokens de presupuesto
    for linea in df.head(presupuesto).to_csv(index=False, header=False).splitlines(keepends=True):
        usado += tokens(linea)
        if usado > presupuesto:
            break
        n += 1
    return n


def resumen_para_prompt(df: pd.DataFrame, max_valores: int = 5) -> str:
    """Resumen compacto de un DataFrame para pegar en un prompt, una línea por columna:
    «nombre (tipo) | nulos=N | distintos=N | ejemplos o rango». Las columnas numéricas o de fecha dan «min…max»;
    las demás, sus `max_valores` valores más frecuentes separados por «; ». Las columnas identificadoras (`id` o
    `*_id`) NO muestran ejemplos: ponen «identificador (sin ejemplos)». Primera línea: «filas=N»."""
    lineas = [f"filas={len(df)}"]
    for c in df.columns:
        s = df[c]
        if c == "id" or c.endswith("_id"):
            detalle = "identificador (sin ejemplos)"
        elif pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s) or pd.api.types.is_datetime64_any_dtype(s):
            detalle = f"{s.min()}…{s.max()}"
        else:
            detalle = "; ".join(map(str, s.value_counts().head(max_valores).index))
        lineas.append(f"{c} ({s.dtype}) | nulos={int(s.isna().sum())} | distintos={s.nunique()} | {detalle}")
    return "\n".join(lineas)


def muestra_estratificada(df: pd.DataFrame, por: str, n: int, semilla: int = 0) -> pd.DataFrame:
    """Muestra de unas `n` filas que conserva la proporción de cada valor de `por` (al menos una fila por valor),
    reproducible con la semilla. Ordenada por el índice original."""
    partes = []
    for _, g in df.groupby(por, observed=True):
        k = max(1, round(n * len(g) / len(df)))
        partes.append(g.sample(n=min(k, len(g)), random_state=semilla))
    return pd.concat(partes).sort_index()


muestra = pedidos.head(10_000)
estimado = tokens(muestra.to_csv(index=False)) * len(pedidos) / len(muestra)
print("CSV completo (estimado con 10.000 filas):", round(estimado), "tokens | resumen:", tokens(resumen_para_prompt(pedidos)), "tokens")
print("filas que caben en 8.000 tokens:", filas_que_caben(pedidos, 8000))
print("coste ilustrativo del CSV completo:", round(coste_eur(round(estimado), 500, 3.0, 15.0), 2), "€")
