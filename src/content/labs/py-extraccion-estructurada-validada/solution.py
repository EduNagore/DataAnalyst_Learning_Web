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
    """Devuelve el objeto JSON de la respuesta del modelo o None si no hay ninguno válido."""
    inicio, fin = respuesta.find("{"), respuesta.rfind("}")
    if inicio == -1 or fin <= inicio:
        return None
    try:
        return json.loads(respuesta[inicio : fin + 1])
    except json.JSONDecodeError:
        return None


def validar(d) -> list[str]:
    """Lista de errores (vacía si es válido)."""
    if not isinstance(d, dict):
        return ["no_es_objeto"]
    errores = [f"falta:{k}" for k in CLAVES if k not in d]
    errores += [f"clave_extra:{k}" for k in d if k not in CLAVES]
    if "tema" in d:
        if not isinstance(d["tema"], str):
            errores.append("tipo_incorrecto:tema")
        elif d["tema"].lower() not in TEMAS:
            errores.append("tema_invalido")
    if "dias_retraso" in d:
        v = d["dias_retraso"]
        if v is not None and (not isinstance(v, int) or isinstance(v, bool)):
            errores.append("tipo_incorrecto:dias_retraso")
        elif v is not None and not 0 <= v <= 365:
            errores.append("dias_fuera_de_rango")
    if "pide_reembolso" in d and not isinstance(d["pide_reembolso"], bool):
        errores.append("tipo_incorrecto:pide_reembolso")
    if "confianza" in d and d["confianza"] not in CONFIANZAS:
        errores.append("confianza_invalida")
    return errores


def extraer(llm, texto: str, max_reintentos: int = 1) -> dict:
    """Pide al modelo la extracción y la valida, con reintentos acotados."""
    prompt = construir_prompt(texto)
    intentos = 0
    while True:
        respuesta = llm.complete(prompt)
        intentos += 1
        datos = parsear_json(respuesta)
        errores = ["sin_json"] if datos is None else validar(datos)
        if not errores:
            datos = dict(datos)
            datos["tema"] = datos["tema"].lower()
            return {"ok": True, "datos": datos, "intentos": intentos, "errores": []}
        if intentos > max_reintentos:
            return {"ok": False, "datos": None, "intentos": intentos, "errores": errores}
        prompt += f"\nTu respuesta anterior no es válida: {', '.join(errores)}. Devuelve solo el JSON corregido."


def tasa_validez(resultados: list[dict]) -> dict:
    """Proporciones sobre el total."""
    n = len(resultados)
    return {
        "primera": sum(r["ok"] and r["intentos"] == 1 for r in resultados) / n,
        "tras_reintento": sum(r["ok"] and r["intentos"] > 1 for r in resultados) / n,
        "descartadas": sum(not r["ok"] for r in resultados) / n,
    }


def dias_regex(texto: str):
    """Número de días que menciona el texto o None."""
    m = re.search(r"(\d+)\s+días?\b", texto)
    return int(m.group(1)) if m else None


def resumen_dias(tabla) -> dict:
    """Número de tickets con días y media de esos días."""
    dias = [d for d in (dias_regex(t) for t in tabla["text"]) if d is not None]
    return {"n": len(dias), "media": round(sum(dias) / len(dias), 2)}


if __name__ == "__main__":
    llm = MockLLM(script=list(RESPUESTAS))
    resultados = [extraer(llm, t) for t in TICKETS]
    print(tasa_validez(resultados))
    print(resumen_dias(load_table("support_tickets")))
