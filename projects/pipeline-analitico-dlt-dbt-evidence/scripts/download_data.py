"""Descarga las tablas de Lumen que usa el proyecto en ./data (Parquet)."""

import urllib.request
from pathlib import Path

BASE = "https://edunagore.github.io/DataAnalyst_Learning_Web/data/lumen/"
TABLES = ["customers", "orders", "order_items", "products", "categories", "returns"]


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "data"
    out.mkdir(exist_ok=True)
    for table in TABLES:
        destino = out / f"{table}.parquet"
        print(f"Descargando {table}...")
        urllib.request.urlretrieve(f"{BASE}{table}.parquet", destino)  # noqa: S310
        print(f"  -> {destino} ({destino.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
