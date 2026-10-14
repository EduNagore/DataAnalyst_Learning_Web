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
    # TODO
    ...


def grafo(modelos: dict[str, str]) -> dict[str, set[str]]:
    """Modelo → conjunto de modelos de los que depende. Lanza ValueError si un ref apunta a un modelo que no existe."""
    # TODO
    ...


def orden_de_ejecucion(modelos: dict[str, str]) -> list[str]:
    """Orden topológico: cada modelo aparece después de todos aquellos de los que depende. Entre los listos,
    alfabético (determinista). Lanza ValueError con la palabra «ciclo» si hay dependencias circulares."""
    # TODO
    ...


def niveles(modelos: dict[str, str]) -> list[list[str]]:
    """Grupos de modelos que se pueden ejecutar en paralelo: nivel 0 = sin dependencias, etc."""
    # TODO
    ...


def afectados(modelos: dict[str, str], cambiados: set[str]) -> set[str]:
    """Los modelos cambiados y todos los que dependen de ellos, directa o indirectamente (`state:modified+`)."""
    # TODO
    ...


def violaciones_de_capas(modelos: dict[str, str]) -> list[tuple[str, str]]:
    """Reglas de la guía de estructura: los modelos `stg_` solo leen fuentes (nunca ref); el resto nunca lee
    fuentes directamente. Devuelve [(modelo, motivo)] ordenado por modelo, con motivos «stg_usa_ref» o «fuente_fuera_de_staging»."""
    # TODO
    ...


print(orden_de_ejecucion(modelos))
print(niveles(modelos))
print("cambia stg_orders →", sorted(afectados(modelos, {"stg_orders"})))
print("violaciones:", violaciones_de_capas(modelos))
