"""Cada lab Python: la solución pasa todos sus tests (≥1 oculto) y el starter NO.

Usa el mismo `runner.py` y la misma librería `datakit` que el navegador
(`public/py/`), con CPython en lugar de Pyodide (PLAN.md §11).
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "public" / "py"))

import runner  # noqa: E402
from datakit import data  # noqa: E402

data.set_data_root(ROOT / "public" / "data")

LABS_DIR = ROOT / "src" / "content" / "labs"
PY_LABS = sorted(p.parent for p in LABS_DIR.glob("*/starter.py"))


def _run(lab: Path, code_file: str) -> dict:
    code = (lab / code_file).read_text(encoding="utf-8")
    tests = (lab / "test_lab.py").read_text(encoding="utf-8")
    return json.loads(runner.run_lab(code, tests))


def test_hay_labs_python():
    assert PY_LABS, "No se encontró ningún lab Python"


@pytest.mark.parametrize("lab", PY_LABS, ids=lambda p: p.name)
def test_la_solucion_pasa_todos_los_tests(lab):
    result = _run(lab, "solution.py")
    assert result["error"] is None, result["error"]
    assert result["tests"], "El lab no tiene tests"
    failed = [t for t in result["tests"] if not t["passed"]]
    assert not failed, f"Tests fallidos con la solución: {failed}"
    assert any(t["hidden"] for t in result["tests"]), "Falta al menos un test oculto"


@pytest.mark.parametrize("lab", PY_LABS, ids=lambda p: p.name)
def test_el_starter_no_pasa(lab):
    result = _run(lab, "starter.py")
    ok = result["error"] is None and result["tests"] and all(t["passed"] for t in result["tests"])
    assert not ok, "El starter ya pasa todos los tests"


@pytest.mark.parametrize("lab", PY_LABS, ids=lambda p: p.name)
def test_metadatos_del_lab(lab):
    front = yaml.safe_load((lab / "index.mdx").read_text(encoding="utf-8").split("---")[1])
    assert front["language"] == "python"
    assert len(front["hints"]) >= 2
    assert (lab / "solution.py").exists() and (lab / "test_lab.py").exists()
