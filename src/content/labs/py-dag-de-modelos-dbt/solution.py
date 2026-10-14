import re

# Proyecto de ejemplo: nombre del modelo → SQL con llamadas a ref() y source()
modelos = {
    "stg_orders": "select * from {{ source('lumen', 'orders') }} where status <> 'cancelado'",
    "stg_order_items": "select * from {{ source('lumen', 'order_items') }}",
    "stg_customers": "select * from {{ source('lumen', 'customers') }}",
    "stg_products": 'select * from {{ source("lumen", "products") }}',
    "int_order_lines": """
        select o.order_id, o.customer_id, o.order_date, oi.product_id, oi.quantity * oi.unit_price as ingresos
        from {{ ref('stg_orders') }} o
        join {{ ref('stg_order_items') }} oi using (order_id)
        join {{ ref('stg_products') }} p using (product_id)""",
    "fct_orders": "select order_id, customer_id, order_date, sum(ingresos) as ingresos from {{ ref('int_order_lines') }} group by 1, 2, 3",
    "dim_customers": "select c.*, count(f.order_id) as pedidos from {{ ref('stg_customers') }} c left join {{ ref( 'fct_orders' ) }} f using (customer_id) group by all",
    "mart_revenue_monthly": "select date_trunc('month', order_date) as mes, sum(ingresos) from {{ ref('fct_orders') }} group by 1",
    "mart_customer_ltv": """
        select d.customer_id, sum(f.ingresos) as ltv
        from {{ ref('dim_customers') }} d join {{ ref('fct_orders') }} f using (customer_id)
        left join {{ source('lumen', 'subscriptions') }} s using (customer_id) group by 1""",
}

_REF = re.compile(r"""ref\(\s*['"]([^'"]+)['"]\s*\)""")
_SOURCE = re.compile(r"""source\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*\)""")


def dependencias(sql: str) -> tuple[set[str], set[tuple[str, str]]]:
    """Devuelve (modelos referenciados con ref, fuentes usadas con source como pares (origen, tabla))."""
    return set(_REF.findall(sql)), set(_SOURCE.findall(sql))


def grafo(modelos: dict[str, str]) -> dict[str, set[str]]:
    """Modelo → conjunto de modelos de los que depende. Lanza ValueError si un ref apunta a un modelo que no existe."""
    g = {}
    for nombre, sql in modelos.items():
        refs, _ = dependencias(sql)
        desconocidos = refs - set(modelos)
        if desconocidos:
            raise ValueError(f"{nombre}: ref a modelos inexistentes {sorted(desconocidos)}")
        g[nombre] = refs
    return g


def orden_de_ejecucion(modelos: dict[str, str]) -> list[str]:
    """Orden topológico: cada modelo aparece después de todos aquellos de los que depende. Entre los listos,
    alfabético (determinista). Lanza ValueError con la palabra «ciclo» si hay dependencias circulares."""
    pendientes = {m: set(d) for m, d in grafo(modelos).items()}
    orden: list[str] = []
    while pendientes:
        listos = sorted(m for m, d in pendientes.items() if not d)
        if not listos:
            raise ValueError(f"ciclo entre {sorted(pendientes)}")
        orden.extend(listos)
        for m in listos:
            del pendientes[m]
        for d in pendientes.values():
            d.difference_update(listos)
    return orden


def niveles(modelos: dict[str, str]) -> list[list[str]]:
    """Grupos de modelos que se pueden ejecutar en paralelo: nivel 0 = sin dependencias, etc."""
    pendientes = {m: set(d) for m, d in grafo(modelos).items()}
    salida: list[list[str]] = []
    while pendientes:
        listos = sorted(m for m, d in pendientes.items() if not d)
        if not listos:
            raise ValueError(f"ciclo entre {sorted(pendientes)}")
        salida.append(listos)
        for m in listos:
            del pendientes[m]
        for d in pendientes.values():
            d.difference_update(listos)
    return salida


def afectados(modelos: dict[str, str], cambiados: set[str]) -> set[str]:
    """Los modelos cambiados y todos los que dependen de ellos, directa o indirectamente (`state:modified+`)."""
    g = grafo(modelos)
    resultado = set(cambiados)
    ampliado = True
    while ampliado:
        ampliado = False
        for m, deps in g.items():
            if m not in resultado and deps & resultado:
                resultado.add(m)
                ampliado = True
    return resultado


def violaciones_de_capas(modelos: dict[str, str]) -> list[tuple[str, str]]:
    """Reglas de la guía de estructura: los modelos `stg_` solo leen fuentes (nunca ref); el resto nunca lee
    fuentes directamente. Devuelve [(modelo, motivo)] ordenado por modelo, con motivos «stg_usa_ref» o «fuente_fuera_de_staging»."""
    fallos = []
    for nombre in sorted(modelos):
        refs, fuentes = dependencias(modelos[nombre])
        if nombre.startswith("stg_") and refs:
            fallos.append((nombre, "stg_usa_ref"))
        if not nombre.startswith("stg_") and fuentes:
            fallos.append((nombre, "fuente_fuera_de_staging"))
    return fallos


print(orden_de_ejecucion(modelos))
print(niveles(modelos))
print("cambia stg_orders →", sorted(afectados(modelos, {"stg_orders"})))
print("violaciones:", violaciones_de_capas(modelos))
