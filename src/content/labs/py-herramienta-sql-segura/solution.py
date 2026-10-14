import hashlib
import re

import duckdb
from datakit.data import load_table

_clientes = load_table("customers")
_pedidos = load_table("orders")
_pedidos = _pedidos[_pedidos["order_date"].dt.year == 2025]
_CON = duckdb.connect()
_CON.register("customers", _clientes)
_CON.register("orders", _pedidos)

POLITICA = {
    "tablas": {"customers", "orders"},
    "max_filas": 1000,
    "prohibidas": {
        "insert", "update", "delete", "drop", "create", "alter", "truncate", "attach", "detach", "copy", "pragma",
        "install", "load", "export", "import", "call", "set", "grant", "revoke", "merge", "replace", "vacuum",
        "checkpoint", "read_csv", "read_parquet", "read_json", "read_text", "glob", "http", "httpfs",
    },
}


def limpiar_sql(sql: str) -> str:
    """Quita los comentarios (`-- …` hasta el fin de línea y `/* … */`), recorta los espacios y elimina un único «;» final."""
    s = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    s = re.sub(r"--[^\n]*", " ", s)
    s = s.strip()
    return s[:-1].strip() if s.endswith(";") else s


def sin_literales(sql: str) -> str:
    """Sustituye el contenido de los literales de texto entre comillas simples (con '' como comilla escapada) por «''»."""
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def validar(sql: str, politica: dict) -> tuple[bool, str]:
    """(True, «ok») si la consulta es aceptable; si no, (False, motivo) con el PRIMER motivo que se encuentre, en este orden:
    «vacia»; «multiples_sentencias» (queda algún «;» fuera de literales); «no_es_select» (no empieza por SELECT o WITH);
    «palabra_prohibida:<palabra>» (alguna palabra de `politica["prohibidas"]` como palabra completa, ignorando literales
    y mayúsculas); «tabla_no_permitida:<tabla>» (alguna tabla tras FROM o JOIN que no esté en `politica["tablas"]` ni sea
    una CTE definida en la propia consulta)."""
    s = limpiar_sql(sql)
    if not s:
        return False, "vacia"
    base = sin_literales(s)
    if ";" in base:
        return False, "multiples_sentencias"
    palabras = re.findall(r"[a-z_][a-z0-9_]*", base.lower())
    if palabras[0] not in ("select", "with"):
        return False, "no_es_select"
    for p in palabras:
        if p in politica["prohibidas"]:
            return False, f"palabra_prohibida:{p}"
    ctes = set(re.findall(r"\b([a-z_][a-z0-9_]*)\s+as\s*\(", base.lower()))
    for tabla in re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_.]*)", base.lower()):
        if tabla not in politica["tablas"] and tabla not in ctes:
            return False, f"tabla_no_permitida:{tabla}"
    return True, "ok"


def ejecutar_seguro(sql: str, politica: dict, con=None) -> dict:
    """Valida y ejecuta. Devuelve {estado, motivo, filas, truncado}: «rechazada» (con el motivo de `validar`, filas = None),
    «error» (la ejecución falló; motivo = primera línea del error) u «ok». Se piden como mucho max_filas + 1 filas con
    LIMIT para saber si hay más: `filas` tiene como mucho `max_filas` y `truncado` es True si había más."""
    ok, motivo = validar(sql, politica)
    if not ok:
        return {"estado": "rechazada", "motivo": motivo, "filas": None, "truncado": False}
    n = politica["max_filas"]
    try:
        df = (con or _CON).execute(f"SELECT * FROM ({limpiar_sql(sql)}) AS q LIMIT {n + 1}").df()
    except Exception as e:  # noqa: BLE001
        return {"estado": "error", "motivo": str(e).splitlines()[0], "filas": None, "truncado": False}
    return {"estado": "ok", "motivo": "ok", "filas": df.head(n), "truncado": len(df) > n}


def registrar(auditoria: list, usuario: str, sql: str, resultado: dict) -> dict:
    """Añade a la lista de auditoría y devuelve una entrada con `usuario`, `sql_hash` (los 12 primeros caracteres del
    SHA-256 de la consulta limpia), `estado`, `motivo` y `n_filas` (0 si no hubo filas). No guarda el SQL ni los datos."""
    entrada = {
        "usuario": usuario,
        "sql_hash": hashlib.sha256(limpiar_sql(sql).encode("utf-8")).hexdigest()[:12],
        "estado": resultado["estado"],
        "motivo": resultado["motivo"],
        "n_filas": 0 if resultado["filas"] is None else len(resultado["filas"]),
    }
    auditoria.append(entrada)
    return entrada


auditoria: list = []
for consulta in (
    "SELECT segment, COUNT(*) AS n FROM customers GROUP BY 1",
    "SELECT 1; DROP TABLE customers",
    "SELECT * FROM read_csv('/etc/passwd')",
    "SELECT * FROM customers",
):
    r = ejecutar_seguro(consulta, POLITICA)
    registrar(auditoria, "analista", consulta, r)
    print(r["estado"], r["motivo"], "| filas:", None if r["filas"] is None else len(r["filas"]), "| truncado:", r["truncado"])
