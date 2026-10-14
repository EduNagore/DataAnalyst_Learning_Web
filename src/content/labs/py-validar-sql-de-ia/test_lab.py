import pandas as pd
from datakit.llm import MockLLM


def test_comparar_resultados(ns):
    """Mismas columnas y filas (en cualquier orden) con tolerancia numérica; distinto nombre de columna o de filas = falso"""
    c = ns["comparar_resultados"]
    a = pd.DataFrame({"canal": ["online", "store"], "total": [100.0, 50.0]})
    assert c(a, a.copy()) and c(a.iloc[::-1].reset_index(drop=True), a)
    assert c(a.assign(total=[100.2, 49.9]), a, tolerancia=0.01) and not c(a.assign(total=[100.2, 49.9]), a, tolerancia=0.001)
    assert not c(a.rename(columns={"total": "t"}), a) and not c(a.iloc[:1], a) and not c(a.assign(canal=["x", "store"]), a)


def test_diagnostico_estatico(ns):
    """Cada candidato defectuoso dispara el aviso que le corresponde; el correcto, ninguno"""
    d = [ns["diagnosticar"](s) for s in ns["CANDIDATOS"]]
    assert d[0] == ["sin_filtro_cancelados", "sin_exclusion_devoluciones"]
    assert d[1] == ["sin_filtro_cancelados"] and d[2] == ["sin_exclusion_devoluciones"]
    assert d[3] == ["sin_cantidad"] and d[4] == []
    assert ns["diagnosticar"]("SELECT 1 FROM returns WHERE cancelado AND year(x) = 2024 AND unit_price > quantity") == ["anio_distinto"]


def test_evaluar_los_cinco_candidatos(ns):
    """Solo el quinto es correcto: el primero falla al ejecutarse (columna inventada) y los otros tres dan cifras plausibles pero erróneas"""
    esperado = ns["esperado"]
    assert abs(esperado["ingresos"].sum() - 45942401.79) < 1
    rs = ns["evaluar_candidatos"](MockLLM(script=list(ns["CANDIDATOS"])), ns["PEDIDO"], esperado, 5)
    assert [r["ok"] for r in rs] == [False, False, False, False, True]
    assert "canal" in rs[0]["error"] and all(r["error"] is None for r in rs[1:])
    assert rs[4]["avisos"] == [] and rs[3]["avisos"] == ["sin_cantidad"]
    totales = [ns["ejecutar"](s)["ingresos"].sum() / 1e6 for s in ns["CANDIDATOS"][1:]]
    assert [round(t, 1) for t in totales] == [47.9, 49.5, 31.5, 45.9]


def test_hidden_respuesta_invalida_y_sin_guion(ns):
    """Una respuesta que no es SQL no detiene la evaluación y se registra como error (test oculto)"""
    esperado = pd.DataFrame({"channel": ["online", "store"], "ingresos": [1.0, 2.0]})
    llm = MockLLM(script=["esto no es SQL"], default="SELECT 'online' AS channel, 1.0 AS ingresos UNION ALL SELECT 'store', 2.0")
    rs = ns["evaluar_candidatos"](llm, "p", esperado, 2)
    assert rs[0]["ok"] is False and rs[0]["error"]
    assert rs[1]["ok"] is True and rs[1]["error"] is None
    assert len(llm.calls) == 2
