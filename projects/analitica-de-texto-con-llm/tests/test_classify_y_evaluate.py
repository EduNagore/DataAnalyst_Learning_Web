import numpy as np
import pytest
from classify import classify_text, cost_eur, parse_and_validate
from evaluate import cohen_kappa, confusion, precision_recall_f1, sample_size


def test_parse_valida_y_normaliza():
    datos, error = parse_and_validate('Aquí va:\n```json\n{"tema": "Pagos", "confianza": "alta"}\n```')
    assert error is None and datos["tema"] == "pagos"


@pytest.mark.parametrize(
    "respuesta",
    ["no sé", '{"tema": "facturacion", "confianza": "alta"}', '{"tema": "app"}', '{"tema": "app", "confianza": "mucha"}'],
)
def test_parse_detecta_errores(respuesta):
    datos, error = parse_and_validate(respuesta)
    assert datos is None and error


def test_reintento_con_el_error_y_suma_de_tokens():
    prompts = []
    respuestas = iter(["basura", '{"tema": "envio", "confianza": "media"}'])

    def falso(prompt: str):
        prompts.append(prompt)
        return next(respuestas), 100, 10

    r = classify_text(falso, "Mi pedido no llega", max_reintentos=1)
    assert r.ok and r.tema == "envio" and r.intentos == 2
    assert r.tokens_entrada == 200 and r.tokens_salida == 20
    assert len(prompts) == 2 and prompts[1] != prompts[0]


def test_sin_reintentos_descarta():
    r = classify_text(lambda p: ("basura", 50, 5), "x", max_reintentos=0)
    assert not r.ok and r.intentos == 1 and r.error


def test_coste():
    assert cost_eur(1_000_000, 500_000, 3.0, 15.0) == pytest.approx(10.5)


def test_matriz_y_metricas():
    m = confusion(["a", "a", "b", "b", "c"], ["a", "a", "a", "b", "c"], ["a", "b", "c"])
    assert m.tolist() == [[2, 0, 0], [1, 1, 0], [0, 0, 1]]
    met = precision_recall_f1(m)
    assert met["precision"][0] == pytest.approx(2 / 3)
    assert met["recall"][1] == pytest.approx(0.5)


def test_kappa_de_la_documentacion_de_scikit_learn():
    y1 = ["neg", "pos", "neg", "neu", "pos"]
    y2 = ["neg", "pos", "neg", "neu", "neg"]
    m = confusion(y1, y2, ["neg", "neu", "pos"])
    assert cohen_kappa(m) == pytest.approx(0.6875)
    assert np.trace(m) == 4


def test_tamano_de_muestra():
    assert sample_size(0.05) == 385
    assert sample_size(0.025) == 1537
