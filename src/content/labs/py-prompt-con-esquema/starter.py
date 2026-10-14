import re

import pandas as pd
from datakit.data import load_table
from datakit.llm import MockLLM
from pandas.api import types as pdt

esquemas = {n: load_table(n) for n in ("orders", "order_items", "returns")}

definiciones = {
    "ingresos_netos": "SUM(order_items.quantity * order_items.unit_price) de los pedidos con status <> 'cancelado' "
    "y de las líneas que NO aparecen en returns",
}

ejemplos = [
    (
        "¿Cuántos pedidos no cancelados hubo en 2025?",
        "SELECT COUNT(*) FROM orders WHERE status <> 'cancelado' AND year(order_date) = 2025;",
    )
]

SQL_CORRECTO = (
    "SELECT o.channel, SUM(oi.quantity * oi.unit_price) AS ingresos_netos FROM orders o "
    "JOIN order_items oi USING (order_id) LEFT JOIN returns r ON r.order_item_id = oi.order_item_id "
    "WHERE o.status <> 'cancelado' AND r.return_id IS NULL AND year(o.order_date) = 2025 GROUP BY 1;"
)
SQL_INGENUO = "SELECT channel, COUNT(*) FROM orders GROUP BY 1; -- sin definiciones de negocio"


def tipo_sql(serie: pd.Series) -> str:
    """BOOLEAN, BIGINT, DOUBLE, TIMESTAMP o VARCHAR según el tipo de la serie."""
    # TODO
    ...


def construir_prompt(pregunta: str, esquemas: dict, definiciones: dict | None = None, ejemplos: list | None = None, dialecto: str = "DuckDB") -> str:
    """Prompt con estas secciones, en este orden y con estos encabezados exactos:
    1) una instrucción inicial que nombra el dialecto («…una única consulta SQL ({dialecto})…»);
    2) «## Esquema»: una línea por tabla, «nombre(col TIPO, col TIPO, …)», con las columnas en su orden;
    3) «## Definiciones de negocio» (solo si hay): «- nombre: definición»;
    4) «## Ejemplos» (solo si hay): «Pregunta: …» y «SQL: …» de cada ejemplo;
    5) «## Reglas»: usar solo tablas y columnas del esquema, no inventar columnas, y responder «NO_PUEDO_RESPONDER» con lo que falta si no hay información suficiente;
    6) «## Pregunta» con la pregunta.
    No incluye NINGUNA fila de datos, solo el esquema."""
    # TODO
    ...


def auditar_prompt(prompt: str, esquemas: dict, presupuesto_tokens: int) -> list[str]:
    """Problemas de un prompt, en este orden: «sin_esquema:<tabla>» por cada tabla del esquema que no aparece nombrada
    como «tabla(»; «datos_personales» si contiene un correo electrónico o un identificador «cust-» seguido de 6 dígitos;
    «sin_regla_de_salida» si no contiene «NO_PUEDO_RESPONDER»; y «excede_presupuesto» si supera el presupuesto de tokens."""
    # TODO
    ...


def asistente_simulado() -> MockLLM:
    """YA IMPLEMENTADA. Un asistente simulado: responde bien solo si el prompt trae la definición de ingresos_netos."""
    return MockLLM(rules=[(r"ingresos_netos: SUM", SQL_CORRECTO)], default=SQL_INGENUO)


pregunta = "¿Cuáles fueron los ingresos netos por canal en 2025?"
con = construir_prompt(pregunta, esquemas, definiciones, ejemplos)
sin = construir_prompt(pregunta, esquemas)
print(con)
print("problemas:", auditar_prompt(con, esquemas, 2000))
print("tokens con definiciones:", MockLLM.count_tokens(con), "| sin:", MockLLM.count_tokens(sin))
print("respuesta con definiciones:", asistente_simulado().complete(con)[:60], "…")
print("respuesta sin definiciones:", asistente_simulado().complete(sin)[:60], "…")
