import re

VERBOS_ACCION = (
    "recomend", "propon", "priori", "aprob", "lanz", "detener", "paralic", "mantener", "reducir", "ampliar", "ajust",
)

ANTES = (
    "Hola, te paso el análisis de 2025. He mirado los pedidos, los clientes y los tickets, y hay varias cosas "
    "interesantes. Los ingresos han subido bastante y hay más clientes. También he visto que la frecuencia ha "
    "subido un poco. Si quieres lo vemos con calma y te enseño los gráficos."
)

DESPUES = (
    "**Recomendación:** priorizar la captación de clientes nuevos en 2027 antes que una subida de precios. Los "
    "ingresos netos de Lumen crecieron un 120 % en 2025 (49,5 M€ frente a 22,4 M€) y el 75 % de ese crecimiento "
    "viene de tener más clientes activos (+81 %); la frecuencia de compra aporta el 24 % y el ticket medio, el 1 %. "
    "Los guardrails están estables (margen del 35,7 %; devoluciones del 6,3 %). **Límite:** la descomposición "
    "describe el pasado y no prueba que invertir más en captación repita ese resultado. **Siguiente paso:** medir "
    "la incrementalidad del gasto de afiliación, el canal con el CAC más alto (163,6 €)."
)


def revisar_resumen(texto: str, max_palabras: int = 120) -> dict:
    """palabras, cifras, empieza_con_recomendacion, tiene_limite, tiene_siguiente_paso, problemas y valido."""
    # TODO
    ...


for nombre, t in (("ANTES", ANTES), ("DESPUES", DESPUES)):
    print(nombre, revisar_resumen(t))
