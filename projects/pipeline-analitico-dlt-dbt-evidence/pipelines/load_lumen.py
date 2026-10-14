"""Carga los Parquet de Lumen en DuckDB (esquema `raw`) con dlt.

Ejecuta:  python pipelines/load_lumen.py
Requisito: haber ejecutado antes scripts/download_data.py
"""

from pathlib import Path

import dlt
import duckdb
import pyarrow as pa

DATA = Path(__file__).resolve().parents[1] / "data"
DB = Path(__file__).resolve().parents[1] / "lumen.duckdb"
TABLES = ["customers", "orders", "order_items", "products", "categories", "returns"]


def parquet_resource(table: str):
    """Un recurso de dlt que lee un Parquet por lotes.

    TODO 1: ¿qué `write_disposition` hace la carga idempotente? ("replace" reescribe la tabla;
            "merge" con `primary_key` actualiza por clave). Elige y justifica en el README.
    """

    @dlt.resource(name=table, write_disposition="replace")
    def _resource():
        con = duckdb.connect()
        reader = con.execute(f"SELECT * FROM read_parquet('{(DATA / f'{table}.parquet').as_posix()}')").fetch_record_batch(
            100_000
        )
        for batch in reader:
            yield pa.Table.from_batches([batch])

    return _resource


@dlt.source(name="lumen")
def lumen_source():
    return [parquet_resource(t) for t in TABLES]


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="lumen",
        destination=dlt.destinations.duckdb(str(DB)),
        dataset_name="raw",
    )
    info = pipeline.run(lumen_source())
    print(info)
    # TODO 2: comprueba que el número de filas de cada tabla coincide con el Parquet de origen.


if __name__ == "__main__":
    main()
