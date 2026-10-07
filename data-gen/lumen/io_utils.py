"""Escritura de archivos y checksums (ver docs/DATASET.md §7)."""

import hashlib
import json
from pathlib import Path

import pandas as pd


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, compression="zstd", index=False)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def compute_checksums(root: Path) -> dict[str, str]:
    checksums = {}
    for file in sorted(root.rglob("*")):
        if file.is_file():
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            checksums[str(file.relative_to(root)).replace("\\", "/")] = digest
    return checksums


def write_checksums(checksums: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checksums, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def total_size_mb(root: Path) -> float:
    return sum(f.stat().st_size for f in root.rglob("*") if f.is_file()) / (1024 * 1024)
