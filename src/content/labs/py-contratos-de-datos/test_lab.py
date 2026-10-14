import pandas as pd


def test_tipo_logico(ns):
    """Mapea los tipos de pandas a bool, int, float, datetime y string"""
    t = ns["tipo_logico"]
    assert t(pd.Series([True, False])) == "bool" and t(pd.Series([1, 2])) == "int"
    assert t(pd.Series([1.5])) == "float" and t(pd.Series(pd.to_datetime(["2025-01-01"]))) == "datetime"
    assert t(pd.Series(["a", "b"])) == "string" and t(pd.Series(["a"], dtype="object")) == "string"


def test_contrato_de_pedidos(ns):
    """Los 392.906 pedidos limpios cumplen el contrato; el export crudo incumple tres cláusulas"""
    assert ns["validar_contrato"](ns["pedidos"], ns["contrato_pedidos"]) == []
    assert ns["validar_contrato"](ns["pedidos_crudos"], ns["contrato_pedidos"]) == [
        ("device", "nulos", 580),
        ("order_date", "tipo", "datetime", "string"),
        ("shipping_cost", "tipo", "float", "string"),
    ]


def test_inferir_y_comparar(ns):
    """Un contrato inferido de los datos se cumple a sí mismo; store_id admite nulos"""
    c = ns["inferir_contrato"](ns["pedidos"])
    assert ns["validar_contrato"](ns["pedidos"], c) == []
    assert c["store_id"]["not_null"] is False and c["order_id"] == {"tipo": "string", "not_null": True}
    assert ns["cambios_incompatibles"](ns["contrato_pedidos"], c) == []


def test_hidden_cambios_que_rompen(ns):
    """Quitar una columna, cambiar un tipo o relajar un not_null rompe a los consumidores; añadir no (test oculto)"""
    v1 = {"a": {"tipo": "int", "not_null": True}, "b": {"tipo": "string", "not_null": True}, "c": {"tipo": "float", "not_null": False}}
    v2 = {
        "a": {"tipo": "string", "not_null": True},
        "b": {"tipo": "string", "not_null": False},
        "d": {"tipo": "bool", "not_null": False},
    }
    assert ns["cambios_incompatibles"](v1, v2) == [("a", "tipo_cambiado"), ("b", "restriccion_eliminada"), ("c", "columna_eliminada")]
    df = pd.DataFrame({"a": [1, 2], "z": ["x", None]})
    assert ns["validar_contrato"](df, v1) == [("b", "falta"), ("c", "falta"), ("z", "sobra")]
    assert ns["validar_contrato"](pd.DataFrame({"a": [1.5, None]}), {"a": {"tipo": "int", "not_null": True}}) == [
        ("a", "tipo", "int", "float"),
        ("a", "nulos", 1),
    ]
