import copy


def test_validar_el_registro_de_lumen(ns):
    """Tres problemas de gobierno: una certificada depende de una no certificada, una obsoleta sigue en un panel y no tiene responsable"""
    assert ns["validar_registro"](ns["registro"]) == [
        ("clientes_activos", "certificada_depende_de_no_certificada", "ventas_totales"),
        ("ingresos_viejos", "obsoleta_en_uso", "campanas"),
        ("ingresos_viejos", "sin_responsable"),
    ]


def test_definiciones_duplicadas(ns):
    """ingresos_brutos y ventas_totales son la misma definición con dos nombres"""
    assert ns["definiciones_duplicadas"](ns["registro"]) == [["ingresos_brutos", "ventas_totales"]]
    assert ns["normalizar"]("  SUM(a *  b) ") == "sum(a * b)"


def test_impacto_de_un_cambio(ns):
    """Cambiar ingresos_brutos afecta a ingresos_netos y ticket_medio y a los paneles ventas y consejo"""
    assert ns["impacto_de_cambio"](ns["registro"], "ingresos_brutos") == {
        "metricas": ["ingresos_netos", "ticket_medio"],
        "paneles": ["consejo", "ventas"],
    }
    assert ns["impacto_de_cambio"](ns["registro"], "ticket_medio") == {"metricas": [], "paneles": ["consejo"]}
    assert ns["impacto_de_cambio"](ns["registro"], "pedidos")["metricas"] == ["ticket_medio"]


def test_hidden_registro_roto(ns):
    """Duplicados de nombre, estados inválidos y dependencias inexistentes (test oculto)"""
    r = copy.deepcopy(ns["registro"][:3])
    r.append({"nombre": "pedidos", "definicion": "COUNT(*)", "responsable": "ops", "estado": "borrador", "depende_de": ["fantasma"], "paneles": []})
    r.append({"nombre": "pedidos", "definicion": "COUNT(1)", "responsable": "ops", "estado": "certificada", "depende_de": [], "paneles": []})
    problemas = ns["validar_registro"](r)
    assert ("pedidos", "nombre_duplicado") in problemas and problemas.count(("pedidos", "nombre_duplicado")) == 1
    assert ("pedidos", "estado_invalido") in problemas
    assert ("pedidos", "dependencia_inexistente", "fantasma") in problemas
    assert problemas == sorted(problemas, key=lambda t: (t[0], t[1], t[2] if len(t) > 2 else ""))
    assert ns["definiciones_duplicadas"]([]) == [] and ns["validar_registro"]([]) == []
    assert ns["impacto_de_cambio"](r[:3], "devoluciones") == {"metricas": ["ingresos_netos"], "paneles": ["ventas", "consejo"][::-1]}
