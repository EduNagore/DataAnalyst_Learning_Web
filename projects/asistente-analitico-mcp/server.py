"""Servidor MCP de solo lectura sobre DuckDB.

Ejecuta:  uv run mcp dev server.py
Comprueba en la documentación del SDK de MCP la API vigente: este esqueleto sigue el ejemplo oficial
(clase `MCPServer` y decorador `@mcp.tool()`).
"""

import hashlib
import json
import time
from pathlib import Path

import duckdb
import yaml
from guard import validate_sql, with_limit
from mcp.server import MCPServer

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "lumen.duckdb"
LOG_PATH = ROOT / "logs" / "audit.jsonl"
METRICS = yaml.safe_load((ROOT / "metrics.yaml").read_text(encoding="utf-8"))

mcp = MCPServer("lumen-analitica")


def connect() -> duckdb.DuckDBPyConnection:
    """Conexión de SOLO LECTURA: aunque falle la validación, la base no se puede modificar."""
    return duckdb.connect(str(DB_PATH), read_only=True)


def audit(tool: str, payload: str, ok: bool, rows: int = 0) -> None:
    """Registro de auditoría: herramienta, hash de la consulta (no el texto), resultado y filas."""
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "ts": time.time(),
        "tool": tool,
        "sha": hashlib.sha256(payload.encode()).hexdigest()[:12],
        "ok": ok,
        "rows": rows,
    }
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


@mcp.tool()
def list_tables() -> list[str]:
    """Lista las tablas disponibles."""
    with connect() as con:
        return [r[0] for r in con.execute("SHOW TABLES").fetchall()]


@mcp.tool()
def describe_table(table: str) -> list[dict]:
    """Columnas y tipos de una tabla permitida."""
    # TODO: valida que `table` está en guard.ALLOWED_TABLES antes de consultar el catálogo.
    raise NotImplementedError


@mcp.tool()
def get_metric(name: str) -> dict:
    """Valor de una métrica gobernada del catálogo (metrics.yaml)."""
    # TODO: busca la métrica, ejecuta su SQL y devuelve {"metric", "value", "description"}; si no existe, di cuáles hay.
    raise NotImplementedError


@mcp.tool()
def run_query(sql: str) -> dict:
    """Ejecuta una consulta SELECT validada, con límite de filas, y devuelve columnas y filas."""
    ok, reason = validate_sql(sql)
    if not ok:
        audit("run_query", sql, False)
        return {"error": reason}
    with connect() as con:
        cur = con.execute(with_limit(sql))
        columns = [d[0] for d in cur.description]
        rows = cur.fetchall()
    audit("run_query", sql, True, len(rows))
    return {"columns": columns, "rows": rows}


if __name__ == "__main__":
    mcp.run()
