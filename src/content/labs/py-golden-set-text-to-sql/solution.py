import math
import numbers

import duckdb
import pandas as pd
from datakit.data import load_table
from datakit.llm import MockLLM

_pedidos = load_table("orders")
_pedidos = _pedidos[_pedidos["order_date"].dt.year == 2025]
_envios = load_table("shipments")
_envios = _envios[_envios["order_id"].isin(_pedidos["order_id"])]
BASE = {"orders": _pedidos, "customers": load_table("customers"), "subscriptions": load_table("subscriptions"), "shipments": _envios}
# Versión alternativa de los datos (se quita 1 de cada 10 filas): una consulta correcta debe acertar en las dos
ALTERNATIVA = {n: df.iloc[[i for i in range(len(df)) if i % 10 != 0]] for n, df in BASE.items()}

_CON = {}
for _v, _tablas in (("base", BASE), ("alternativa", ALTERNATIVA)):
    _CON[_v] = duckdb.connect()
    for _n, _df in _tablas.items():
        _CON[_v].register(_n, _df)

ORO = [
    {"id": "q01", "pregunta": "¿Cuántos pedidos no cancelados hubo en 2025?",
     "sql": "SELECT COUNT(*) FROM orders WHERE status <> 'cancelado'"},
    {"id": "q02", "pregunta": "Pedidos no cancelados de 2025 por canal",
     "sql": "SELECT channel, COUNT(*) FROM orders WHERE status <> 'cancelado' GROUP BY 1"},
    {"id": "q03", "pregunta": "Clientes por segmento",
     "sql": "SELECT segment, COUNT(*) FROM customers GROUP BY 1"},
    {"id": "q04", "pregunta": "¿Cuántos clientes tienen consentimiento de marketing?",
     "sql": "SELECT COUNT(*) FROM customers WHERE marketing_consent"},
    {"id": "q05", "pregunta": "Suscripciones activas a 31-05-2026 por plan",
     "sql": "SELECT plan, COUNT(*) FROM subscriptions WHERE started_at <= DATE '2026-05-31' AND (cancelled_at IS NULL OR cancelled_at > DATE '2026-05-31') GROUP BY 1"},
    {"id": "q06", "pregunta": "MRR total de las suscripciones activas a 31-05-2026",
     "sql": "SELECT SUM(mrr_eur) FROM subscriptions WHERE started_at <= DATE '2026-05-31' AND (cancelled_at IS NULL OR cancelled_at > DATE '2026-05-31')"},
    {"id": "q07", "pregunta": "¿Cuántos envíos de pedidos de 2025 llegaron con retraso?",
     "sql": "SELECT COUNT(*) FROM shipments WHERE actual_date > promised_date"},
    {"id": "q08", "pregunta": "Pedidos no cancelados de 2025 por dispositivo",
     "sql": "SELECT device, COUNT(*) FROM orders WHERE status <> 'cancelado' GROUP BY 1"},
    {"id": "q09", "pregunta": "Coste medio de envío de los pedidos no cancelados de 2025",
     "sql": "SELECT AVG(shipping_cost) FROM orders WHERE status <> 'cancelado'"},
    {"id": "q10", "pregunta": "Clientes dados de alta en 2025 por canal de adquisición",
     "sql": "SELECT acquisition_channel, COUNT(*) FROM customers WHERE year(signup_date) = 2025 GROUP BY 1"},
]

# Lo que contesta el sistema evaluado (simulado): una por pregunta, en orden
RESPUESTAS = [
    "SELECT 161706",  # q01: valor fijo escrito a mano: acierta en los datos base por casualidad
    "SELECT channel, COUNT(*) FROM orders GROUP BY 1",  # q02: olvida excluir cancelados
    "SELECT COUNT(*) AS n, segment FROM customers GROUP BY segment",  # q03: correcta (otro orden y alias)
    "SELECT COUNT(*) FROM customers WHERE consent = TRUE",  # q04: columna inventada
    "SELECT plan, COUNT(*) FROM subscriptions WHERE cancelled_at IS NULL GROUP BY 1",  # q05: ignora las bajas posteriores a la fecha
    "SELECT SUM(mrr_eur) FROM subscriptions WHERE started_at <= DATE '2026-05-31' AND (cancelled_at IS NULL OR cancelled_at > DATE '2026-05-31')",  # q06: correcta
    "NO_PUEDO_RESPONDER: no sé qué significa «con retraso»",  # q07: se abstiene
    "SELECT device AS d, COUNT(*) AS n FROM orders WHERE status != 'cancelado' GROUP BY 1",  # q08: correcta
    "SELECT AVG(shipping_cost) FROM orders",  # q09: olvida excluir cancelados
    "SELECT acquisition_channel, COUNT(*) FROM customers WHERE year(signup_date) = 2025 GROUP BY 1",  # q10: correcta
]


def ejecutar(sql: str, version: str = "base") -> pd.DataFrame:
    """YA IMPLEMENTADA. Ejecuta una consulta sobre la versión «base» o «alternativa» de los datos."""
    return _CON[version].execute(sql).df()


def mismo_resultado(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    """¿Devuelven lo mismo? Compara el conjunto de filas ignorando el nombre y el orden de las columnas y el orden
    de las filas. Cada valor se normaliza a texto (los números, redondeados a 2 decimales) y cada fila se convierte
    en la tupla ordenada de sus valores. También deben coincidir las dimensiones (filas × columnas)."""

    def normal(v):
        if isinstance(v, numbers.Number) and not isinstance(v, bool):
            return str(round(float(v), 2))
        return str(v)

    def filas(df):
        return sorted(tuple(sorted(normal(v) for v in fila)) for fila in df.itertuples(index=False, name=None))

    return a.shape == b.shape and filas(a) == filas(b)


def evaluar_pregunta(sql_oro: str, respuesta: str) -> str:
    """Categoría del resultado de una respuesta, en este orden de comprobación:
    «abstencion» si empieza por NO_PUEDO_RESPONDER; «error_ejecucion» si la consulta falla en cualquier versión;
    «correcta» si coincide con la consulta de oro en las versiones «base» y «alternativa»;
    «correcta_por_casualidad» si coincide en la base pero no en la alternativa; y «resultado_distinto» si no coincide en la base."""
    if respuesta.strip().upper().startswith("NO_PUEDO_RESPONDER"):
        return "abstencion"
    try:
        coincide = {}
        for v in ("base", "alternativa"):
            coincide[v] = mismo_resultado(ejecutar(respuesta, v), ejecutar(sql_oro, v))
    except Exception:  # noqa: BLE001
        return "error_ejecucion"
    if coincide["base"] and coincide["alternativa"]:
        return "correcta"
    if coincide["base"]:
        return "correcta_por_casualidad"
    return "resultado_distinto"


def evaluar_sistema(llm: MockLLM, oro: list) -> list[dict]:
    """Pregunta al sistema cada pregunta del conjunto de oro y devuelve, por pregunta, `id`, `categoria` y `sql`."""
    salida = []
    for item in oro:
        sql = llm.complete(item["pregunta"])
        salida.append({"id": item["id"], "categoria": evaluar_pregunta(item["sql"], sql), "sql": sql})
    return salida


def exactitud(resultados: list[dict], estricta: bool = True) -> float:
    """Fracción de preguntas correctas. Con estricta=True solo cuenta «correcta»; con False, también
    «correcta_por_casualidad» (lo que daría una evaluación que solo mira los datos base)."""
    buenas = {"correcta"} if estricta else {"correcta", "correcta_por_casualidad"}
    return sum(r["categoria"] in buenas for r in resultados) / len(resultados)


def intervalo_wilson(aciertos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianza de Wilson para una proporción (aciertos de n)."""
    p = aciertos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - margen, centro + margen


resultados = evaluar_sistema(MockLLM(script=list(RESPUESTAS)), ORO)
for r in resultados:
    print(r["id"], r["categoria"])
print("exactitud estricta:", exactitud(resultados), "| solo datos base:", exactitud(resultados, estricta=False))
print("IC 95 % de Wilson:", tuple(round(x, 2) for x in intervalo_wilson(round(10 * exactitud(resultados)), 10)))
