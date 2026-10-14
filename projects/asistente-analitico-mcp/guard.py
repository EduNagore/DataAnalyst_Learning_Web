"""Validador de consultas SQL de solo lectura. Implementa los TODO y haz pasar `pytest`."""

from __future__ import annotations

import re

ALLOWED_TABLES = {"customers", "orders", "order_items", "products", "categories", "returns", "shipments", "subscriptions"}
FORBIDDEN_WORDS = {
    "insert", "update", "delete", "drop", "alter", "create", "attach", "copy", "pragma", "install", "load",
    "export", "import", "call", "set",
}  # fmt: skip
FORBIDDEN_FUNCTIONS = ("read_csv", "read_parquet", "read_json", "glob(", "read_text", "httpfs")
MAX_ROWS = 1000


def strip_literals(sql: str) -> str:
    """Sustituye el contenido de los literales entre comillas simples por vacío para no confundir palabras con datos."""
    # TODO
    raise NotImplementedError


def validate_sql(sql: str) -> tuple[bool, str]:
    """(ok, motivo). Motivos: 'vacia', 'multiples_sentencias', 'no_es_select', 'palabra_prohibida:x',
    'funcion_prohibida:x', 'tabla_no_permitida:x' u 'ok'.

    Reglas: una sola sentencia; debe empezar por SELECT o WITH; sin palabras de escritura o de sistema;
    sin funciones de acceso a ficheros; solo tablas de ALLOWED_TABLES (cuidado con los alias y los CTE).
    Comprueba siempre sobre el texto SIN literales.
    """
    # TODO
    raise NotImplementedError


def with_limit(sql: str, max_rows: int = MAX_ROWS) -> str:
    """Envuelve la consulta para devolver como máximo `max_rows` filas."""
    # TODO
    raise NotImplementedError


__all__ = ["ALLOWED_TABLES", "MAX_ROWS", "re", "strip_literals", "validate_sql", "with_limit"]
