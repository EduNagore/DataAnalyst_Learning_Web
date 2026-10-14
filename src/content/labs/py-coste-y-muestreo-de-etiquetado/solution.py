import math

from datakit.data import load_table
from datakit.llm import MockLLM

TICKETS = load_table("support_tickets")

PROMPT_BASE = (
    "Clasifica el ticket de atención al cliente en una de estas etiquetas y responde solo con la etiqueta.\n"
    "- envio: retrasos, paquetes perdidos o incompletos, seguimiento.\n"
    "- pagos: cobros, facturas, tarjetas, cupones y descuentos.\n"
    "- devoluciones: devolver o cambiar un artículo, reembolsos.\n"
    "- producto: calidad, descripción, tallas, información del artículo.\n"
    "- app: fallos de la aplicación (sesión, carrito, notificaciones).\n"
    "Si ninguna encaja, responde «otro»."
)
PRECIO_ENTRADA = 3.00  # € por millón de tokens de entrada (ficticio, solo para el ejercicio)
PRECIO_SALIDA = 15.00  # € por millón de tokens de salida (ficticio, solo para el ejercicio)


def tokens(texto: str) -> int:
    """YA IMPLEMENTADA. Aproximación del simulador: un token cada cuatro caracteres (mínimo 1)."""
    return MockLLM.count_tokens(texto)


def coste_llamada(tokens_entrada: int, tokens_salida: int, precio_entrada: float, precio_salida: float) -> float:
    """Euros de una llamada; los precios son € por millón de tokens."""
    return (tokens_entrada * precio_entrada + tokens_salida * precio_salida) / 1_000_000


def plan_de_coste(textos, prompt_base: str, tokens_salida: int, precio_entrada: float, precio_salida: float, deduplicar: bool = False) -> dict:
    """Plan de una clasificación: una llamada por texto (o por texto distinto si `deduplicar`), con prompt = prompt_base + «\nTicket: » + texto.
    Devuelve {"llamadas": int, "tokens_entrada": int, "tokens_salida": int, "coste": float}."""
    lista = list(dict.fromkeys(textos)) if deduplicar else list(textos)
    t_in = sum(tokens(prompt_base + "\nTicket: " + t) for t in lista)
    t_out = tokens_salida * len(lista)
    return {
        "llamadas": len(lista),
        "tokens_entrada": t_in,
        "tokens_salida": t_out,
        "coste": coste_llamada(t_in, t_out, precio_entrada, precio_salida),
    }


def margen_error(p: float, n: int, z: float = 1.96) -> float:
    """Margen de error de una proporción (aproximación normal): z · √(p(1−p)/n)."""
    return z * math.sqrt(p * (1 - p) / n)


def tamano_muestra(margen: float, p: float = 0.5, z: float = 1.96) -> int:
    """Menor n entero con margen de error ≤ `margen` para una proporción p (por defecto, el peor caso p = 0,5)."""
    return math.ceil(z**2 * p * (1 - p) / margen**2)


def asignar_muestra(conteos: dict, n_total: int, minimo: int) -> dict:
    """Muestra estratificada: a cada clase, max(minimo, round(n_total · su proporción)), sin superar el nº de casos de la clase."""
    total = sum(conteos.values())
    return {c: min(n, max(minimo, round(n_total * n / total))) for c, n in conteos.items()}


if __name__ == "__main__":
    textos = list(TICKETS["text"])
    todo = plan_de_coste(textos, PROMPT_BASE, 3, PRECIO_ENTRADA, PRECIO_SALIDA)
    unico = plan_de_coste(textos, PROMPT_BASE, 3, PRECIO_ENTRADA, PRECIO_SALIDA, deduplicar=True)
    print(todo)
    print(unico)
    print(tamano_muestra(0.05), tamano_muestra(0.025), tamano_muestra(0.01))
