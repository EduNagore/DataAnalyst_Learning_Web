#!/usr/bin/env python
"""Genera el dataset "Lumen" completo (ver docs/DATASET.md).

Uso:
    uv run python data-gen/generate.py
    uv run python data-gen/generate.py --config data-gen/config.yaml --out public/data

Determinista: la misma config produce siempre los mismos bytes (por eso
`checksums.json` puede usarse en CI para detectar una regeneración que ya
no sea reproducible).
"""

import argparse
from pathlib import Path

import yaml
from lumen.build import build_lumen, build_raw_variant, write_all
from lumen.extra_datasets import load_extra_datasets

MAX_TOTAL_MB = 60


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "config.yaml")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent.parent / "public" / "data")
    parser.add_argument(
        "--checksums",
        type=Path,
        default=Path(__file__).parent / "checksums.json",
        help="Dónde escribir el manifiesto de checksums (por defecto, data-gen/checksums.json).",
    )
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))

    print(f"Generando Lumen (seed={config['seed']}, escala={config['scale']['main']})...")
    main_tables = build_lumen(config, config["seed"], config["scale"]["main"])

    print(f"Generando lumen_variant (seed={config['variant_seed']}, escala={config['scale']['variant']})...")
    variant_tables = build_lumen(config, config["variant_seed"], config["scale"]["variant"])

    print("Generando lumen_raw (corrompiendo una muestra de las tablas principales)...")
    raw_tables = build_raw_variant(config, config["seed"], main_tables)

    print("Cargando datasets externos verificados (extra/)...")
    extra_tables = load_extra_datasets()

    if args.out.exists():
        import shutil

        shutil.rmtree(args.out)

    print(f"Escribiendo en {args.out}...")
    result = write_all(args.out, main_tables, variant_tables, raw_tables, extra_tables)

    from lumen.io_utils import write_checksums

    write_checksums(result["checksums"], args.checksums)

    print(f"\nListo. Tamaño total: {result['size_mb']:.1f} MB (límite: {MAX_TOTAL_MB} MB).")
    if result["size_mb"] > MAX_TOTAL_MB:
        print(
            f"ATENCIÓN: se ha superado el límite de {MAX_TOTAL_MB} MB de PLAN.md §3. "
            "Reduce sizes.web_sessions / events_target en config.yaml."
        )

    print("\nFilas por tabla (lumen/):")
    for name, df in main_tables.items():
        print(f"  {name:<24} {len(df):>10,}")


if __name__ == "__main__":
    main()
