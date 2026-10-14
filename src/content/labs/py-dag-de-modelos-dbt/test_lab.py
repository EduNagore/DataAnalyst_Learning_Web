def test_dependencias(ns):
    """Extrae ref() y source() con comillas simples o dobles y espacios libres"""
    refs, fuentes = ns["dependencias"]("select * from {{ ref( 'a' ) }} join {{ref(\"b\")}} using (id) join {{ source('x', \"t\") }}")
    assert refs == {"a", "b"} and fuentes == {("x", "t")}
    assert ns["dependencias"]("select 1") == (set(), set())
    m = ns["modelos"]
    assert ns["dependencias"](m["int_order_lines"])[0] == {"stg_orders", "stg_order_items", "stg_products"}
    assert ns["dependencias"](m["stg_products"])[1] == {("lumen", "products")}


def test_orden_y_niveles(ns):
    """Nueve modelos en cinco niveles; cada modelo va después de sus dependencias"""
    m = ns["modelos"]
    orden = ns["orden_de_ejecucion"](m)
    assert len(orden) == 9 and set(orden) == set(m)
    for nombre, deps in ns["grafo"](m).items():
        assert all(orden.index(d) < orden.index(nombre) for d in deps)
    assert ns["niveles"](m) == [
        ["stg_customers", "stg_order_items", "stg_orders", "stg_products"],
        ["int_order_lines"],
        ["fct_orders"],
        ["dim_customers", "mart_revenue_monthly"],
        ["mart_customer_ltv"],
    ]


def test_ejecucion_selectiva_y_capas(ns):
    """Si cambia stg_orders se reconstruyen 6 modelos; si cambia stg_customers, 3; un mart lee una fuente directamente"""
    m = ns["modelos"]
    assert ns["afectados"](m, {"stg_orders"}) == {
        "stg_orders", "int_order_lines", "fct_orders", "dim_customers", "mart_revenue_monthly", "mart_customer_ltv",
    }
    assert ns["afectados"](m, {"stg_customers"}) == {"stg_customers", "dim_customers", "mart_customer_ltv"}
    assert ns["afectados"](m, {"mart_revenue_monthly"}) == {"mart_revenue_monthly"}
    assert ns["violaciones_de_capas"](m) == [("mart_customer_ltv", "fuente_fuera_de_staging")]


def test_hidden_ciclos_y_referencias_rotas(ns):
    """Dependencias circulares, referencias a modelos inexistentes y staging que usa ref (test oculto)"""
    ciclo = {"a": "select * from {{ ref('b') }}", "b": "select * from {{ ref('c') }}", "c": "select * from {{ ref('a') }}", "z": "select 1"}
    try:
        ns["orden_de_ejecucion"](ciclo)
        fallo = False
    except ValueError as e:
        fallo = "ciclo" in str(e)
    assert fallo, "Debe lanzar ValueError mencionando el ciclo."
    try:
        ns["grafo"]({"a": "select * from {{ ref('no_existe') }}"})
        roto = False
    except ValueError as e:
        roto = "no_existe" in str(e)
    assert roto
    malo = {"stg_x": "select * from {{ ref('stg_y') }}", "stg_y": "select * from {{ source('s', 't') }}"}
    assert ns["violaciones_de_capas"](malo) == [("stg_x", "stg_usa_ref")]
    assert ns["afectados"]({"a": "select 1", "b": "select * from {{ ref('a') }}", "c": "select * from {{ ref('b') }}"}, {"a"}) == {"a", "b", "c"}
