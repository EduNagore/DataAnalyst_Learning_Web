"""Libros Excel de práctica: la solución marca ✔ en todo y el libro de trabajo no.

Se calculan con la librería `formulas` (sin Excel). Limitación conocida: la coerción de texto a número
difiere de la de Excel, así que el error «número guardado como texto» de `auditoria-de-un-modelo` solo
se aprecia en Excel; aquí exigimos al menos 6 de los 8 controles en ✘.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from openpyxl import load_workbook

formulas = pytest.importorskip("formulas")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "workbooks"
IDS = [
    "matrices-dinamicas-y-buscarx",
    "let-lambda-escenarios",
    "agrupar-y-pivotar",
    "auditoria-de-un-modelo",
    "verificar-el-trabajo-de-una-ia",
]


@pytest.fixture(scope="module", autouse=True)
def built():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-workbooks.py")], check=True, cwd=ROOT)


def _results(path: Path) -> list[str]:
    model = formulas.ExcelModel().loads(str(path)).finish()
    model.calculate()
    with tempfile.TemporaryDirectory() as tmp:
        model.write(dirpath=tmp)
        wb = load_workbook(next(Path(tmp).glob("*")), data_only=True)
    ws = next(w for w in wb.worksheets if w.title.upper() == "COMPROBACION")
    cells = (ws.cell(row=r, column=5).value for r in range(4, ws.max_row + 1))
    return [v for v in cells if v]


@pytest.mark.parametrize("wid", IDS)
def test_solucion_todo_correcto(wid):
    res = _results(OUT / f"{wid}-solucion.xlsx")
    assert res and all(r == "✔" for r in res), f"{wid}: {res}"


TASK_IDS = IDS[:3]
MODEL_IDS = IDS[3:]


@pytest.mark.parametrize("wid", TASK_IDS)
def test_trabajo_en_blanco_no_puntua(wid):
    res = _results(OUT / f"{wid}.xlsx")
    assert res and set(res) == {"—"}, f"{wid}: {res}"


@pytest.mark.parametrize("wid", MODEL_IDS)
def test_modelo_con_errores_falla_controles(wid):
    res = _results(OUT / f"{wid}.xlsx")
    assert res.count("✘") >= 5, f"{wid}: {res}"
