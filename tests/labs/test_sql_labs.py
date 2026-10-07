"""Cada lab SQL: la solución pasa sus checks y el starter NO (ver PLAN.md §11).

Ejecuta las consultas con DuckDB de CPython sobre los mismos Parquet que usa
el navegador. La comparación replica la semántica de `src/lib/resultCompare.ts`
(multiconjunto por defecto, tolerancia de floats, subconjunto de columnas).
"""

import re
from pathlib import Path

import duckdb
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
LABS_DIR = ROOT / "src" / "content" / "labs"
DATA_DIR = ROOT / "public" / "data"
TABLES = [p.stem for p in (DATA_DIR / "lumen").glob("*.parquet")]

SQL_LABS = sorted(p.parent for p in LABS_DIR.glob("*/starter.sql"))


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("CREATE SCHEMA IF NOT EXISTS variant")
    for table in TABLES:
        main = (DATA_DIR / "lumen" / f"{table}.parquet").as_posix()
        variant = (DATA_DIR / "lumen_variant" / f"{table}.parquet").as_posix()
        con.execute(f"CREATE VIEW main.{table} AS SELECT * FROM read_parquet('{main}')")
        con.execute(f"CREATE VIEW variant.{table} AS SELECT * FROM read_parquet('{variant}')")
    return con


def _run(con, sql: str, schema: str):
    con.execute(f"SET search_path = '{schema}'")
    cursor = con.execute(sql)
    columns = [d[0] for d in cursor.description]
    return columns, cursor.fetchall()


def _normalize(columns, rows, compare: dict):
    wanted = compare.get("columns") or columns
    if compare.get("ignoreColumnNames"):
        idx = list(range(len(columns)))
    else:
        missing = [c for c in wanted if c not in columns]
        if missing:
            return None  # faltan columnas: no coincide
        idx = [columns.index(c) for c in wanted]
    tol = compare.get("floatTolerance", 1e-6)

    def cell(v):
        return round(v / tol) * tol if isinstance(v, float) and tol else v

    out = [tuple(cell(r[i]) for i in idx) for r in rows]
    return out if compare.get("orderMatters") else sorted(out, key=repr)


def _matches(expected, actual, compare: dict) -> bool:
    e = _normalize(*expected, compare)
    a = _normalize(*actual, compare)
    return e is not None and a is not None and e == a


def _checks(lab: Path) -> dict:
    return yaml.safe_load((lab / "checks.yaml").read_text(encoding="utf-8")) or {}


@pytest.fixture(scope="module")
def con():
    return _connect()


def test_hay_labs_sql():
    assert SQL_LABS, "No se encontró ningún lab SQL"


@pytest.mark.parametrize("lab", SQL_LABS, ids=lambda p: p.name)
def test_la_solucion_devuelve_datos_y_cumple_sus_propias_aserciones(con, lab):
    solution = (lab / "solution.sql").read_text(encoding="utf-8")
    columns, rows = _run(con, solution, "main")
    assert rows, "La solución no devuelve filas sobre el dataset principal"

    # Como en el navegador, las aserciones de texto ignoran los comentarios.
    searchable = re.sub(r"--[^\n]*", "", solution).lower()
    for a in _checks(lab).get("assertions", []):
        found = a["value"].lower() in searchable
        if a["kind"] == "query-text-contains":
            assert found, f"La solución incumple su aserción «{a['name']}»"
        else:
            assert not found, f"La solución incumple su aserción «{a['name']}»"


@pytest.mark.parametrize("lab", SQL_LABS, ids=lambda p: p.name)
def test_el_starter_no_pasa(con, lab):
    solution = _run(con, (lab / "solution.sql").read_text(encoding="utf-8"), "main")
    compare = _checks(lab).get("compare", {})
    try:
        starter = _run(con, (lab / "starter.sql").read_text(encoding="utf-8"), "main")
    except duckdb.Error:
        return  # un starter que no ejecuta tampoco pasa
    assert not _matches(solution, starter, compare), "El starter ya coincide con la solución"


@pytest.mark.parametrize("lab", SQL_LABS, ids=lambda p: p.name)
def test_el_test_oculto_detecta_hardcodeo(con, lab):
    """Con hiddenOnVariant, la solución debe dar un resultado distinto en la variante
    (si no, una respuesta con las cifras copiadas pasaría el test oculto)."""
    if not _checks(lab).get("hiddenOnVariant"):
        pytest.skip("El lab no usa test oculto")
    solution = (lab / "solution.sql").read_text(encoding="utf-8")
    compare = _checks(lab).get("compare", {})
    main = _run(con, solution, "main")
    variant = _run(con, solution, "variant")
    assert not _matches(main, variant, compare), (
        "La solución da lo mismo en lumen y lumen_variant: el test oculto no protege nada"
    )


@pytest.mark.parametrize("lab", SQL_LABS, ids=lambda p: p.name)
def test_los_datasets_declarados_existen(lab):
    text = (lab / "index.mdx").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    for table in front["datasets"]:
        assert table in TABLES, f"{table} no es una tabla de lumen/"
    for hint in front["hints"]:
        assert hint.strip(), "pista vacía"
    assert len(front["hints"]) >= 2, "cada lab necesita al menos 2 pistas"
