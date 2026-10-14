import re

import duckdb
import pandas as pd
from datakit.data import load_table
from datakit.llm import MockLLM

_pedidos = load_table("orders")
_pedidos = _pedidos[_pedidos["order_date"].dt.year == 2025]  # el pedido es de 2025: se trabaja solo con ese año
_lineas = load_table("order_items")
_lineas = _lineas[_lineas["order_id"].isin(_pedidos["order_id"])]
_devol = load_table("returns")
TABLAS = {"orders": _pedidos, "order_items": _lineas, "returns": _devol[_devol["order_item_id"].isin(_lineas["order_item_id"])]}
_CON = duckdb.connect()
for _nombre, _df in TABLAS.items():
    _CON.register(_nombre, _df)
PEDIDO = "Ingresos netos por canal en 2025 (sin pedidos cancelados y sin líneas devueltas)"

# Respuestas guionizadas de un asistente simulado: cuatro con fallo y una correcta
CANDIDATOS = [
    # 1. Alucina una columna que no existe
    "SELECT o.canal, SUM(oi.quantity * oi.unit_price) AS ingresos FROM orders o JOIN order_items oi USING (order_id) "
    "WHERE year(o.order_date) = 2025 GROUP BY 1",
    # 2. Olvida excluir los pedidos cancelados
    "SELECT o.channel, SUM(oi.quantity * oi.unit_price) AS ingresos FROM orders o JOIN order_items oi USING (order_id) "
    "LEFT JOIN returns r ON r.order_item_id = oi.order_item_id WHERE r.return_id IS NULL AND year(o.order_date) = 2025 GROUP BY 1",
    # 3. Olvida excluir las líneas devueltas
    "SELECT o.channel, SUM(oi.quantity * oi.unit_price) AS ingresos FROM orders o JOIN order_items oi USING (order_id) "
    "WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025 GROUP BY 1",
    # 4. Olvida multiplicar por la cantidad
    "SELECT o.channel, SUM(oi.unit_price) AS ingresos FROM orders o JOIN order_items oi USING (order_id) "
    "LEFT JOIN returns r ON r.order_item_id = oi.order_item_id WHERE o.status <> 'cancelado' AND r.return_id IS NULL "
    "AND year(o.order_date) = 2025 GROUP BY 1",
    # 5. Correcta
    "SELECT o.channel, SUM(oi.quantity * oi.unit_price) AS ingresos FROM orders o JOIN order_items oi USING (order_id) "
    "LEFT JOIN returns r ON r.order_item_id = oi.order_item_id WHERE o.status <> 'cancelado' AND r.return_id IS NULL "
    "AND year(o.order_date) = 2025 GROUP BY 1",
]


def ejecutar(sql: str) -> pd.DataFrame:
    """YA IMPLEMENTADA. Ejecuta una consulta con DuckDB sobre los pedidos de 2025 de Lumen (tablas orders, order_items
    y returns) y devuelve un DataFrame. La conexión se crea una sola vez."""
    return _CON.execute(sql).df()


def comparar_resultados(obtenido: pd.DataFrame, esperado: pd.DataFrame, tolerancia: float = 0.005) -> bool:
    """True si ambos DataFrames tienen las mismas columnas (mismo orden), las mismas filas (ignorando el orden de las
    filas, ordenando por las columnas no numéricas) y los valores numéricos coinciden con una tolerancia relativa."""
    if list(obtenido.columns) != list(esperado.columns) or len(obtenido) != len(esperado):
        return False
    claves = [c for c in esperado.columns if not pd.api.types.is_numeric_dtype(esperado[c])]
    a = obtenido.sort_values(claves).reset_index(drop=True) if claves else obtenido.reset_index(drop=True)
    b = esperado.sort_values(claves).reset_index(drop=True) if claves else esperado.reset_index(drop=True)
    for c in esperado.columns:
        if c in claves:
            if not (a[c].astype(str) == b[c].astype(str)).all():
                return False
        elif not ((a[c] - b[c]).abs() <= tolerancia * b[c].abs().clip(lower=1e-9)).all():
            return False
    return True


def diagnosticar(sql: str) -> list[str]:
    """Avisos estáticos sobre una consulta para el pedido PEDIDO, en este orden: «sin_filtro_cancelados» si no menciona
    «cancelado»; «sin_exclusion_devoluciones» si no menciona «returns»; «sin_cantidad» si usa unit_price pero no
    quantity; «anio_distinto» si compara year(...) con un año que no es 2025."""
    s = sql.lower()
    avisos = []
    if "cancelado" not in s:
        avisos.append("sin_filtro_cancelados")
    if "returns" not in s:
        avisos.append("sin_exclusion_devoluciones")
    if "unit_price" in s and "quantity" not in s:
        avisos.append("sin_cantidad")
    if any(a != "2025" for a in re.findall(r"year\([^)]*\)\s*=\s*(\d{4})", s)):
        avisos.append("anio_distinto")
    return avisos


def evaluar_candidatos(llm: MockLLM, prompt: str, esperado: pd.DataFrame, n: int) -> list[dict]:
    """Pide `n` respuestas al asistente y evalúa cada una: devuelve una lista de diccionarios con `sql`, `ok` (el resultado
    coincide con `esperado`), `error` (texto del error de ejecución o None) y `avisos` (diagnóstico estático).
    Una consulta que falla al ejecutarse cuenta como no correcta, no detiene la evaluación."""
    resultados = []
    for _ in range(n):
        sql = llm.complete(prompt)
        try:
            ok, error = comparar_resultados(ejecutar(sql), esperado), None
        except Exception as e:  # noqa: BLE001
            ok, error = False, str(e).splitlines()[0]
        resultados.append({"sql": sql, "ok": ok, "error": error, "avisos": diagnosticar(sql)})
    return resultados


esperado = ejecutar(CANDIDATOS[-1])
rs = evaluar_candidatos(MockLLM(script=list(CANDIDATOS)), PEDIDO, esperado, len(CANDIDATOS))
for i, r in enumerate(rs, 1):
    print(i, "OK" if r["ok"] else "MAL", r["error"] or "", r["avisos"])
