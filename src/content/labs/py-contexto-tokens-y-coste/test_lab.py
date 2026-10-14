import pandas as pd


def test_tokens_y_coste(ns):
    """Las primeras 10.000 filas son 184.000 tokens: el CSV completo, ≈ 7,2 millones (≈ 21,7 € de entrada con precios de ejemplo)"""
    muestra = ns["pedidos"].head(10_000)
    t = ns["tokens"](muestra.to_csv(index=False))
    assert 180_000 < t < 190_000
    estimado = t * len(ns["pedidos"]) / len(muestra)
    assert 7_000_000 < estimado < 7_500_000
    assert ns["tokens"]("abcd") == 1 and ns["tokens"]("") == 1
    assert abs(ns["coste_eur"](7238481, 500, 3.0, 15.0) - 21.7225) < 0.001
    assert ns["coste_eur"](1_000_000, 0, 3.0, 15.0) == 3.0 and ns["coste_eur"](0, 1_000_000, 3.0, 15.0) == 15.0


def test_filas_que_caben(ns):
    """En 8.000 tokens caben solo unas 440 de las 392.906 filas; con 100 tokens, ninguna si ni cabe la cabecera"""
    p = ns["pedidos"]
    assert abs(ns["filas_que_caben"](p, 8000) - 440) <= 10, "≈ 440 filas (el formato de fecha de to_csv varía un poco entre versiones)"
    assert ns["filas_que_caben"](p, 5) == 0
    assert ns["filas_que_caben"](p, 80_000) > ns["filas_que_caben"](p, 8000) * 9


def test_resumen_para_prompt(ns):
    """El resumen de 10 líneas ocupa menos de 250 tokens (frente a 7,2 millones) y no muestra identificadores"""
    r = ns["resumen_para_prompt"](ns["pedidos"])
    lineas = r.splitlines()
    assert lineas[0] == "filas=392906" and len(lineas) == 10
    assert ns["tokens"](r) < 250
    assert sum("identificador (sin ejemplos)" in x for x in lineas) == 3, "order_id, customer_id y store_id"
    assert "order-0000000" not in r and "cust-" not in r
    tienda = next(x for x in lineas if x.startswith("store_id"))
    assert "nulos=365198" in tienda
    canal = next(x for x in lineas if x.startswith("channel"))
    assert "distintos=2" in canal and "online" in canal
    fecha = next(x for x in lineas if x.startswith("order_date"))
    assert "2023-01-" in fecha and "2026-06-30" in fecha


def test_muestra_estratificada(ns):
    """Una muestra de 1.000 pedidos conserva la proporción de canales (≈ 7 % tienda) y es reproducible"""
    p = ns["pedidos"]
    m = ns["muestra_estratificada"](p, "channel", 1000)
    assert abs(len(m) - 1000) <= 2 and abs((m["channel"] == "store").sum() - 71) <= 2
    assert m.index.is_monotonic_increasing
    assert m.equals(ns["muestra_estratificada"](p, "channel", 1000))
    assert not m.equals(ns["muestra_estratificada"](p, "channel", 1000, semilla=1))


def test_hidden_caso_pequeno(ns):
    """Estratos pequeños, nulos y columnas booleanas a mano (test oculto)"""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "grupo": ["a"] * 8 + ["b"] + ["c"],
            "importe": [10.0, 20.0, None, 5.0, 1.0, 2.0, 3.0, 4.0, 100.0, 7.5],
            "activo": [True, False] * 5,
        }
    )
    m = ns["muestra_estratificada"](df, "grupo", 4)
    assert set(m["grupo"]) == {"a", "b", "c"}, "Cada estrato aparece al menos una vez."
    r = ns["resumen_para_prompt"](df).splitlines()
    assert r[0] == "filas=10" and "identificador (sin ejemplos)" in r[1]
    assert "nulos=1" in r[3] and "1.0…100.0" in r[3]
    assert "True" in r[4] and "…" not in r[4], "Las booleanas muestran valores, no rango."
    assert ns["filas_que_caben"](df, 10_000) == 10
