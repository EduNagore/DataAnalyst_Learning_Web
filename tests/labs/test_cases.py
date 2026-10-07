"""Las respuestas numéricas de cada caso guiado se recalculan con DuckDB (PLAN.md §11).

Cada caso `src/content/cases/<id>.mdx` tiene un sidecar `<id>.verify.yaml` con una
consulta por paso numérico. Aquí se ejecutan sobre el dataset real y se comparan con
`answer` (dentro de `tolerance`): si el dataset cambia, el caso deja de ser válido y
este test falla en vez de dejar al alumno con una respuesta "correcta" que ya no lo es.
"""

from pathlib import Path

import duckdb
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "src" / "content" / "cases"
DATA_DIR = ROOT / "public" / "data" / "lumen"

CASES = sorted(CASES_DIR.glob("*.mdx"))


def _frontmatter(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])


def _connect(datasets: list[str]) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for table in datasets:
        file = (DATA_DIR / f"{table}.parquet").as_posix()
        con.execute(f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{file}')")
    return con


def _tolerance(step: dict) -> float:
    tol = step.get("tolerance", 0)
    if isinstance(tol, str) and tol.startswith("rel:"):
        return abs(float(step["answer"])) * float(tol[4:])
    return float(tol)


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.stem)
def test_las_respuestas_numericas_se_recalculan(case):
    front = _frontmatter(case)
    verify = yaml.safe_load(case.with_suffix(".verify.yaml").read_text(encoding="utf-8")) or {}
    con = _connect(front["datasets"])
    numeric = [s for s in front["steps"] if s["answerType"] == "numeric"]
    assert numeric, "El caso no tiene pasos numéricos"
    for step in numeric:
        assert step["id"] in verify, f"Falta la consulta de verificación del paso {step['id']}"
        value = con.execute(verify[step["id"]]).fetchone()[0]
        assert abs(float(value) - float(step["answer"])) <= _tolerance(step), (
            f"Paso {step['id']}: la respuesta publicada es {step['answer']} pero los datos dan {value}"
        )


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.stem)
def test_estructura_del_caso(case):
    front = _frontmatter(case)
    ids = [s["id"] for s in front["steps"]]
    assert len(ids) == len(set(ids)), "ids de paso duplicados"
    assert len(front["rubric"]) >= 3, "la rúbrica necesita al menos 3 criterios"
    assert front["modelReport"].strip(), "falta el informe modelo"
    for step in front["steps"]:
        assert step["hints"], f"el paso {step['id']} no tiene pistas"
        if step["answerType"] in ("single", "multiple"):
            options = step["options"]
            answers = step["answer"] if isinstance(step["answer"], list) else [step["answer"]]
            assert all(0 <= a < len(options) for a in answers), f"respuesta fuera de rango en {step['id']}"
        if step["answerType"] == "numeric":
            assert "tolerance" in step, f"el paso numérico {step['id']} necesita tolerance explícita"
        if step["tool"] == "sql":
            for table in front["datasets"]:
                assert (DATA_DIR / f"{table}.parquet").exists()
