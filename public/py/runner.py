"""Ejecuta el código de un alumno y los tests de un lab; devuelve JSON.

Contrato (ver PLAN.md §7.4):
  run_lab(student_code, test_code) -> str (JSON)
  {
    "stdout": "...",                     # lo que imprimió el código del alumno
    "error": null | "mensaje",          # error al ejecutar el código del alumno
    "tests": [{"name", "passed", "message", "hidden"}]
  }

Los tests son funciones `test_*(ns)` donde `ns` es el espacio de nombres del
alumno (sus funciones y variables). Las que empiezan por `test_hidden_` se
marcan como ocultas. El nombre mostrado es la primera línea de su docstring.
"""

import contextlib
import io
import json
import traceback

_STUDENT_FILE = "<tu-codigo>"


def _format_error(exc: BaseException) -> str:
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == _STUDENT_FILE:
            line = frame.lineno
    where = f" (línea {line} de tu código)" if line else ""
    return f"{type(exc).__name__}: {exc}{where}"


def run_lab(student_code: str, test_code: str = "") -> str:
    result = {"stdout": "", "error": None, "tests": []}
    ns: dict = {"__name__": "__student__"}
    buffer = io.StringIO()

    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            exec(compile(student_code, _STUDENT_FILE, "exec"), ns)
        except BaseException as exc:  # noqa: BLE001 — queremos mostrar cualquier error del alumno
            result["error"] = _format_error(exc)
    result["stdout"] = buffer.getvalue()

    if result["error"] is None and test_code:
        test_ns: dict = {"__name__": "__tests__"}
        exec(compile(test_code, "<tests>", "exec"), test_ns)
        for name, fn in list(test_ns.items()):
            if not (name.startswith("test_") and callable(fn)):
                continue
            title = (fn.__doc__ or name).strip().splitlines()[0]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    fn(ns)
                result["tests"].append(
                    {"name": title, "passed": True, "message": "Correcto.", "hidden": name.startswith("test_hidden_")}
                )
            except AssertionError as exc:
                result["tests"].append(
                    {"name": title, "passed": False, "message": str(exc) or "No se cumple la condición.", "hidden": name.startswith("test_hidden_")}
                )
            except BaseException as exc:  # noqa: BLE001
                result["tests"].append(
                    {"name": title, "passed": False, "message": f"Error al ejecutar tu código: {_format_error(exc)}", "hidden": name.startswith("test_hidden_")}
                )
    return json.dumps(result, ensure_ascii=False)
