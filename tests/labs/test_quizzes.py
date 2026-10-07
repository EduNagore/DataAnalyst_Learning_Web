"""Integridad de todos los quizzes (los errores de clave de respuesta son los más caros: se enseña algo falso)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
QUIZ_FILES = sorted((ROOT / "src" / "content" / "quizzes").rglob("*.yaml"))
LESSONS_DIR = ROOT / "src" / "content" / "lessons"


def _questions():
    for f in QUIZ_FILES:
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        for q in data["questions"]:
            yield f, data["lesson"], q


ALL = list(_questions())


def test_hay_quizzes():
    assert ALL


def test_ids_unicos():
    ids = [q["id"] for _, _, q in ALL]
    assert len(ids) == len(set(ids)), "ids de pregunta duplicados"


@pytest.mark.parametrize("f,lesson,q", ALL, ids=lambda x: x["id"] if isinstance(x, dict) else None)
def test_pregunta_bien_formada(f, lesson, q):
    qtype = q["type"]
    answers = q["answer"] if isinstance(q["answer"], list) else [q["answer"]]
    assert q["explanation"].strip(), "falta explicación"
    assert (LESSONS_DIR / f"{lesson}.mdx").exists(), f"lección inexistente: {lesson}"

    if qtype == "numeric":
        assert "tolerance" in q, "numeric necesita tolerance explícita"
        assert len(answers) == 1
        return

    options = q["options"]
    assert len(options) >= 2
    assert all(0 <= a < len(options) for a in answers), "respuesta fuera de rango"
    if qtype in ("single", "sql-output", "formula-output", "chart-critique"):
        assert len(answers) == 1, "una sola respuesta correcta"
        assert len(options) >= 3 or qtype == "truefalse"
    elif qtype == "truefalse":
        assert len(options) == 2 and len(answers) == 1
    elif qtype == "multiple":
        assert 1 <= len(answers) < len(options), "multiple: al menos una correcta y no todas"
        assert len(set(answers)) == len(answers)
    elif qtype == "order":
        assert sorted(answers) == list(range(len(options))), "order: debe ser una permutación completa"


def test_refs_apuntan_a_encabezados_existentes():
    """El ancla `ref` debe existir como encabezado de su lección (slug estilo GitHub)."""
    import re

    def slug(h: str) -> str:
        h = re.sub(r"[`*~]", "", h.lower().strip())
        h = re.sub(r"[^\w\s-]", "", h, flags=re.UNICODE)
        return re.sub(r"-+", "-", re.sub(r"\s+", "-", h)).strip("-")

    missing = []
    for _, lesson, q in ALL:
        ref = q.get("ref")
        if not ref:
            continue
        text = (LESSONS_DIR / f"{lesson}.mdx").read_text(encoding="utf-8")
        body = text.split("---", 2)[2]
        anchors = {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", body, re.MULTILINE)}
        if ref.lstrip("#") not in anchors:
            missing.append((q["id"], ref))
    assert not missing, f"anclas inexistentes: {missing}"
