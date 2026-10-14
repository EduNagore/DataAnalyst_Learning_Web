"""Descarga las tablas de Lumen y crea la base DuckDB de solo lectura `lumen.duckdb`."""

import urllib.request
from pathlib import Path

import duckdb

BASE = "https://edunagore.github.io/DataAnalyst_Learning_Web/data/lumen/"
TABLES = ["customers", "orders", "order_items", "products", "categories", "returns", "shipments", "subscriptions"]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "data"
    out.mkdir(exist_ok=True)
    for table in TABLES:
        destino = out / f"{table}.parquet"
        print(f"Descargando {table}...")
        urllib.request.urlretrieve(f"{BASE}{table}.parquet", destino)  # noqa: S310
    db = root / "lumen.duckdb"
    con = duckdb.connect(str(db))
    for table in TABLES:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet('{(out / f'{table}.parquet').as_posix()}')")
    con.close()
    print(f"Base creada: {db}. Ábrela siempre con read_only=True en el servidor.")


if __name__ == "__main__":
    main()
