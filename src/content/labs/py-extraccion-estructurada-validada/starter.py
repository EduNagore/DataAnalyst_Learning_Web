import json
import re

from datakit.data import load_table
from datakit.llm import MockLLM

TEMAS = ["envio", "pagos", "devoluciones", "producto", "app", "otro"]
CONFIANZAS = ["alta", "media", "baja"]
CLAVES = ["tema", "dias_retraso", "pide_reembolso", "confianza"]

TICKETS = [
    "Mi pedido lleva 8 días de retraso y no tengo ninguna noticia del transportista.",
    "La tarjeta fue rechazada pero el importe se retuvo igualmente.",
    "Quiero devolver un producto, ¿cómo genero la etiqueta de devolución?",
    "La aplicación se cierra sola al intentar pagar.",
    "El producto llegó roto dentro de la caja.",
    "Llevo 14 días esperando el reembolso de mi devolución.",
]

# Respuestas del «modelo» a cada llamada, en orden (el modelo simulado las va consumiendo).
RESPUESTAS = [
    '{"tema": "envio", "dias_retraso": 8, "pide_reembolso": false, "confianza": "alta"}',
    'Aquí tienes el resultado:\n```json\n{"tema": "pagos", "dias_retraso": null, "pide_reembolso": false, "confianza": "alta"}\n```',
    '{"tema": "facturacion", "dias_retraso": null, "pide_reembolso": false, "confianza": "media"}',
    '{"tema": "devoluciones", "dias_retraso": null, "pide_reembolso": false, "confianza": "alta"}',
    "No puedo clasificar este mensaje.",
    '{"tema": "app", "dias_retraso": null, "pide_reembolso": false}',
    '{"tema": "Producto", "dias_retraso": null, "pide_reembolso": true, "confianza": "media"}',
    '{"tema": "devoluciones", "dias_retraso": 999, "pide_reembolso": true, "confianza": "alta"}',
    '{"tema": "devoluciones", "dias_retraso": 14, "pide_reembolso": true, "confianza": "alta"}',
]


def construir_prompt(texto: str) -> str:
    """YA IMPLEMENTADA. Instrucción con el esquema esperado y el ticket."""
    return (
        "Extrae del ticket un objeto JSON con las claves "
        f"{', '.join(CLAVES)}. tema ∈ {TEMAS}; dias_retraso: entero o null; "
        "pide_reembolso: booleano; confianza ∈ " + str(CONFIANZAS) + ".\n"
        f"Ticket: {texto}"
    )


def parsear_json(respuesta: str):
    """Devuelve el objeto JSON de la respuesta del modelo o None si no hay ninguno válido. Tolera vallas de código
    (```json … ```) y texto alrededor: se toma desde la primera «{» hasta la última «}»."""
    # TODO
    ...


def validar(d) -> list[str]:
    """Lista de errores (vacía si es válido), en este orden: «no_es_objeto» (y se para) si d no es un diccionario;
    «falta:<clave>» por cada clave de CLAVES ausente (en el orden de CLAVES); «clave_extra:<clave>» por cada clave que no
    está en CLAVES; «tipo_incorrecto:tema» si tema no es texto o «tema_invalido» si no está en TEMAS (sin distinguir
    mayúsculas); «tipo_incorrecto:dias_retraso» si no es None ni un entero (los booleanos no cuentan) o
    «dias_fuera_de_rango» si no está entre 0 y 365; «tipo_incorrecto:pide_reembolso» si no es booleano;
    «confianza_invalida» si no está en CONFIANZAS. Solo se validan las claves presentes."""
    # TODO
    ...


def extraer(llm, texto: str, max_reintentos: int = 1) -> dict:
    """Pide al modelo la extracción y la valida. Si es inválida, repite la petición hasta `max_reintentos` veces
    añadiendo al prompt anterior, en una línea nueva: «Tu respuesta anterior no es válida: <errores separados por coma>.
    Devuelve solo el JSON corregido.». Si no hay JSON, el error es «sin_json». Devuelve
    {"ok": bool, "datos": dict | None, "intentos": int, "errores": lista de errores del último intento ([] si ok)}.
    En los datos, `tema` se normaliza a minúsculas."""
    # TODO
    ...


def tasa_validez(resultados: list[dict]) -> dict:
    """Proporciones sobre el total: «primera» (ok en el primer intento), «tras_reintento» (ok con más de un intento) y
    «descartadas» (no ok)."""
    # TODO
    ...


def dias_regex(texto: str):
    """Número de días que menciona el texto («8 días», «1 día») como entero o None si no menciona ninguno. Una
    expresión regular es más barata, rápida y exacta que un LLM para este patrón."""
    # TODO
    ...


def resumen_dias(tabla) -> dict:
    """Sobre la columna `text` de la tabla de tickets: número de tickets en los que `dias_regex` encuentra un número y
    media de esos días, redondeada a 2 decimales: {"n": …, "media": …}."""
    # TODO
    ...


if __name__ == "__main__":
    llm = MockLLM(script=list(RESPUESTAS))
    resultados = [extraer(llm, t) for t in TICKETS]
    print(tasa_validez(resultados))
    print(resumen_dias(load_table("support_tickets")))
