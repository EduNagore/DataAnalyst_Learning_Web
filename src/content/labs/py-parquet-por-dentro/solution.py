import io

import pandas as pd
import pyarrow.parquet as pq
from datakit.data import load_table

orders = load_table("orders")


def a_csv(df: pd.DataFrame) -> bytes:
    """El DataFrame como texto CSV (UTF-8, sin índice)."""
    return df.to_csv(index=False).encode("utf-8")


def a_parquet(df: pd.DataFrame, filas_por_grupo: int = 50_000, compresion: str = "zstd") -> bytes:
    """El DataFrame como fichero Parquet en memoria, con grupos de filas del tamaño indicado."""
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, row_group_size=filas_por_grupo, compression=compresion)
    return buf.getvalue()


def bytes_por_columna(parquet: bytes) -> pd.Series:
    """Bytes comprimidos que ocupa cada columna en todo el fichero, de mayor a menor."""
    md = pq.ParquetFile(io.BytesIO(parquet)).metadata
    total: dict[str, int] = {}
    for g in range(md.num_row_groups):
        for j in range(md.num_columns):
            col = md.row_group(g).column(j)
            total[col.path_in_schema] = total.get(col.path_in_schema, 0) + col.total_compressed_size
    return pd.Series(total).sort_values(ascending=False)


def grupos_a_leer(parquet: bytes, columna: str, desde, hasta) -> list[int]:
    """Índices de los grupos de filas que pueden contener valores de `columna` entre `desde` y `hasta`
    (ambos incluidos), usando solo las estadísticas mínimo/máximo del pie del fichero."""
    md = pq.ParquetFile(io.BytesIO(parquet)).metadata
    j = [md.row_group(0).column(k).path_in_schema for k in range(md.num_columns)].index(columna)
    elegidos = []
    for g in range(md.num_row_groups):
        st = md.row_group(g).column(j).statistics
        if st is None or not st.has_min_max or (st.max >= pd.Timestamp(desde) and st.min <= pd.Timestamp(hasta)):
            elegidos.append(g)
    return elegidos


def fraccion_leida(parquet: bytes, columnas: list[str], grupos: list[int]) -> float:
    """Fracción de los bytes comprimidos del fichero que hay que leer para las `columnas` en esos `grupos`."""
    md = pq.ParquetFile(io.BytesIO(parquet)).metadata
    nombres = [md.row_group(0).column(k).path_in_schema for k in range(md.num_columns)]
    total = sum(md.row_group(g).column(k).total_compressed_size for g in range(md.num_row_groups) for k in range(md.num_columns))
    leido = sum(md.row_group(g).column(nombres.index(c)).total_compressed_size for g in grupos for c in columnas)
    return leido / total


ordenado = orders.sort_values("order_date").reset_index(drop=True)
desordenado = orders.sort_values("customer_id").reset_index(drop=True)
pq_ord, pq_des = a_parquet(ordenado), a_parquet(desordenado)
print("CSV:", round(len(a_csv(ordenado)) / 1e6, 1), "MB | Parquet:", round(len(pq_ord) / 1e6, 1), "MB")
print(bytes_por_columna(pq_ord).head(3).to_dict())
g1, g2 = grupos_a_leer(pq_ord, "order_date", "2026-03-01", "2026-03-31"), grupos_a_leer(pq_des, "order_date", "2026-03-01", "2026-03-31")
print("grupos a leer (ordenado por fecha):", g1, "| (ordenado por cliente):", g2)
print("fracción leída:", round(fraccion_leida(pq_ord, ["order_date", "status"], g1), 4))
