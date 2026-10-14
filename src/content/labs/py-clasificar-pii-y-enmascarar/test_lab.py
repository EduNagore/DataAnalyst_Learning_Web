import pandas as pd


def test_validadores(ns):
    """DNI con letra de control, correo con forma válida e IBAN español con control módulo 97"""
    assert ns["es_dni"]("12345678Z") and ns["es_dni"]("00000000T") and not ns["es_dni"]("12345678A")
    assert not ns["es_dni"]("1234567Z") and not ns["es_dni"]("") and ns["es_dni"](" 87654321x ")
    assert ns["es_email"]("ana.perez@correo.es") and not ns["es_email"]("ana@correo") and not ns["es_email"]("a b@c.es")
    assert ns["es_iban_es"]("ES9121000418450200051332") and ns["es_iban_es"]("ES91 2100 0418 4502 0005 1332")
    assert not ns["es_iban_es"]("ES9121000418450200051333") and not ns["es_iban_es"]("FR9121000418450200051332")


def test_clasificar_las_columnas(ns):
    """En el export de soporte hay 4 identificadores directos y 1 cuasi-identificador; en clientes, 1 indirecto y 3 cuasi"""
    c = {col: ns["clasificar_columna"](ns["soporte"][col]) for col in ns["soporte"].columns}
    assert c == {
        "ticket": "ninguno",
        "nombre": "identificador_directo",
        "email": "identificador_directo",
        "dni": "identificador_directo",
        "iban": "identificador_directo",
        "region": "cuasi_identificador",
        "texto": "ninguno",
    }
    cl = ns["load_table"]("customers")
    k = {col: ns["clasificar_columna"](cl[col]) for col in cl.columns}
    assert k["customer_id"] == "identificador_indirecto"
    assert [col for col, v in k.items() if v == "cuasi_identificador"] == ["signup_date", "region", "province"]


def test_enmascarar_y_politicas(ns):
    """Máscaras de correo, DNI e IBAN, y qué ve cada rol"""
    assert ns["enmascarar"]("ana.perez@correo.es", "email") == "a***@correo.es"
    assert ns["enmascarar"]("12345678Z", "dni") == "****678Z"
    m = ns["enmascarar"]("ES9121000418450200051332", "iban")
    assert m.startswith("ES**") and m.endswith("1332") and len(m) == 24 and set(m[4:-4]) == {"*"}
    c = {col: ns["clasificar_columna"](ns["soporte"][col]) for col in ns["soporte"].columns}
    assert ns["politica_de_acceso"](c, "finanzas") == dict.fromkeys(c, "ver")
    s = ns["politica_de_acceso"](c, "soporte")
    assert s["email"] == "enmascarar" and s["region"] == "ver" and s["texto"] == "ver"
    a = ns["politica_de_acceso"](c, "analista")
    assert a["dni"] == "ocultar" and a["nombre"] == "ocultar" and a["region"] == "ver"


def test_hidden_umbral_y_roles(ns):
    """El umbral del 80 %, las columnas vacías y los roles desconocidos (test oculto)"""
    mezcla = pd.Series(["12345678Z", "00000000T", "87654321X", "11111111H", "basura"], name="doc")
    assert ns["clasificar_columna"](mezcla) == "identificador_directo", "4 de 5 valores válidos = 80 %"
    pocos = pd.Series(["12345678Z", "x", "y", "z"], name="doc")
    assert ns["clasificar_columna"](pocos) == "ninguno"
    assert ns["clasificar_columna"](pd.Series([None, None], name="order_id", dtype="object")) == "identificador_indirecto"
    assert ns["clasificar_columna"](pd.Series(["a"], name="fecha_alta")) == "cuasi_identificador"
    assert ns["politica_de_acceso"]({"order_id": "identificador_indirecto"}, "analista") == {"order_id": "enmascarar"}
    for llamada in (lambda: ns["politica_de_acceso"]({}, "becario"), lambda: ns["enmascarar"]("x", "telefono")):
        try:
            llamada()
            fallo = False
        except ValueError:
            fallo = True
        assert fallo
