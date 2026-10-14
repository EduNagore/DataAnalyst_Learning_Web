import copy


def test_metricas_simples_y_derivadas(ns):
    """2025: ingresos netos 45.942.402 € (los mismos que la cuenta de resultados), 161.706 pedidos y 39.190 clientes"""
    c, m = ns["consultar"], ns["modelo"]
    assert abs(c(m, "ingresos_netos", filtros={"anio": 2025}).iloc[0, 0] - 45942401.79) < 1
    assert int(c(m, "pedidos", filtros={"anio": 2025}).iloc[0, 0]) == 161706
    assert int(c(m, "clientes", filtros={"anio": 2025}).iloc[0, 0]) == 39190
    por_anio = c(m, "ingresos_netos", por=["anio"]).set_index("anio")["ingresos_netos"]
    assert list(por_anio.index) == [2023, 2024, 2025, 2026] and abs(por_anio[2024] - 20890553.71) < 1


def test_ratios_y_dimensiones(ns):
    """Ticket medio 2025: 284,37 € online y 280,64 € en tienda; tasa de devolución de Electrónica 7,17 %"""
    c, m = ns["consultar"], ns["modelo"]
    t = c(m, "ticket_medio", por=["canal"], filtros={"anio": 2025}).set_index("canal")["ticket_medio"]
    assert abs(t["online"] - 284.3733) < 0.01 and abs(t["store"] - 280.6359) < 0.01
    d = c(m, "tasa_devolucion", por=["categoria"], filtros={"anio": 2025}).set_index("categoria")["tasa_devolucion"]
    assert len(d) == 8 and abs(d["cat-00"] - 0.0717) < 0.0005
    bi = c(m, "ingresos_netos", por=["canal", "dispositivo"], filtros={"anio": 2025, "canal": ["online"]})
    assert set(bi["canal"]) == {"online"} and len(bi) == 3 and abs(bi["ingresos_netos"].sum() - 14997178.89 - 24746155.07 - 3010202.57) < 2


def test_una_sola_definicion(ns):
    """Los ingresos netos por canal suman el total: la métrica se define una vez y todas las consultas coinciden"""
    c, m = ns["consultar"], ns["modelo"]
    total = c(m, "ingresos_netos", filtros={"anio": 2025}).iloc[0, 0]
    assert abs(c(m, "ingresos_netos", por=["canal"], filtros={"anio": 2025})["ingresos_netos"].sum() - total) < 1
    assert abs(c(m, "ingresos_netos", por=["categoria"], filtros={"anio": 2025})["ingresos_netos"].sum() - total) < 1


def test_hidden_metricas_anidadas_y_filtros_seguros(ns):
    """Una métrica nueva se apoya en otras; un filtro con comilla simple no rompe el SQL; una métrica inexistente falla (test oculto)"""
    m = copy.deepcopy(ns["modelo"])
    m["metricas"]["ingresos_por_cliente"] = {"tipo": "ratio", "numerador": "ingresos_netos", "denominador": "clientes"}
    m["metricas"]["margen_devuelto"] = {"tipo": "derivada", "expr": "devoluciones / ingresos_brutos * 100"}
    v = ns["consultar"](m, "ingresos_por_cliente", filtros={"anio": 2025}).iloc[0, 0]
    assert abs(v - 45942401.79 / 39190) < 0.01
    assert abs(ns["consultar"](m, "margen_devuelto", filtros={"anio": 2025}).iloc[0, 0] - 100 * 3518354.85 / 49460756.64) < 0.01
    sql = ns["generar_sql"](m, "pedidos", por=["canal"], filtros={"canal": "o'neil"})
    assert "o''neil" in sql and len(ns["consultar"](m, "pedidos", por=["canal"], filtros={"canal": "o'neil"})) == 0
    try:
        ns["expresion_metrica"](m, "no_existe")
        fallo = False
    except KeyError:
        fallo = True
    assert fallo
