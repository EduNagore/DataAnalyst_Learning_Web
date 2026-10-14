import re

import duckdb
import pandas as pd
from datakit.data import load_table

TABLAS = {n: load_table(n) for n in ("orders", "order_items", "products", "returns")}

# Modelo semántico: UNA vez la forma de unir las tablas, las dimensiones, las medidas y las métricas
modelo = {
    "base": """
        SELECT o.order_id, o.customer_id, o.order_date, o.channel, o.device,
               oi.quantity, oi.unit_price, p.category_id, (r.return_id IS NOT NULL) AS devuelta
        FROM orders o
        JOIN order_items oi USING (order_id)
        JOIN products p USING (product_id)
        LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
        WHERE o.status <> 'cancelado'""",
    "dimensiones": {
        "anio": "year(order_date)",
        "mes": "date_trunc('month', order_date)",
        "canal": "channel",
        "dispositivo": "device",
        "categoria": "left(category_id, 6)",
    },
    "medidas": {
        "ingresos_brutos": "SUM(quantity * unit_price)",
        "devoluciones": "COALESCE(SUM(quantity * unit_price) FILTER (WHERE devuelta), 0)",
        "pedidos": "COUNT(DISTINCT order_id)",
        "clientes": "COUNT(DISTINCT customer_id)",
    },
    "metricas": {
        "ingresos_brutos": {"tipo": "simple", "medida": "ingresos_brutos"},
        "pedidos": {"tipo": "simple", "medida": "pedidos"},
        "clientes": {"tipo": "simple", "medida": "clientes"},
        "devoluciones": {"tipo": "simple", "medida": "devoluciones"},
        "ingresos_netos": {"tipo": "derivada", "expr": "ingresos_brutos - devoluciones"},
        "ticket_medio": {"tipo": "ratio", "numerador": "ingresos_netos", "denominador": "pedidos"},
        "tasa_devolucion": {"tipo": "ratio", "numerador": "devoluciones", "denominador": "ingresos_brutos"},
    },
}


def literal(valor) -> str:
    """YA IMPLEMENTADA. Valor como literal SQL seguro: texto entre comillas con las comillas simples duplicadas."""
    if isinstance(valor, str):
        return "'" + valor.replace("'", "''") + "'"
    return str(valor)


def expresion_metrica(modelo: dict, nombre: str) -> str:
    """Expresión SQL agregada de una métrica, resolviendo recursivamente otras métricas y medidas.
    simple → la medida; derivada → su `expr` sustituyendo cada nombre de métrica por su expresión entre paréntesis;
    ratio → (numerador) / NULLIF((denominador), 0). Lanza KeyError si la métrica no existe."""
    # TODO
    ...


def generar_sql(modelo: dict, metrica: str, por=(), filtros=None) -> str:
    """SQL de una consulta semántica sobre la tabla `base` (la consulta base del modelo, ya materializada):
    SELECT <dimensiones>, <metrica> AS <metrica> FROM base [WHERE ...] [GROUP BY ...] [ORDER BY ...].
    `filtros` es {dimensión: valor o lista de valores} y se combina con AND (IN para listas). Cada dimensión se
    nombra por su alias en el SELECT; GROUP BY y ORDER BY usan las posiciones 1, 2…"""
    # TODO
    ...


_CONEXIONES: dict = {}


def consultar(modelo: dict, metrica: str, por=(), filtros=None) -> pd.DataFrame:
    """YA IMPLEMENTADA. Ejecuta la consulta semántica con DuckDB. Materializa la consulta base del modelo una sola
    vez (tabla `base`) y reutiliza esa conexión en las consultas siguientes."""
    if modelo["base"] not in _CONEXIONES:
        con = duckdb.connect()
        for nombre, df in TABLAS.items():
            con.register(nombre, df)
        con.execute(f"CREATE TABLE base AS {modelo['base']}")
        _CONEXIONES[modelo["base"]] = con
    return _CONEXIONES[modelo["base"]].execute(generar_sql(modelo, metrica, por, filtros)).df()


print(consultar(modelo, "ingresos_netos", filtros={"anio": 2025}))
print(consultar(modelo, "ticket_medio", por=["canal"], filtros={"anio": 2025}))
