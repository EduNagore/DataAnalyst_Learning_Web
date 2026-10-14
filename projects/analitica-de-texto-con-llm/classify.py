"""Clasificación de tickets con un LLM: salida validada, reintentos acotados y coste. Implementa los TODO."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

TEMAS = ["envio", "pagos", "devoluciones", "producto", "app", "otro"]
CONFIANZAS = ["alta", "media", "baja"]

# Un «cliente LLM» es una función prompt -> (respuesta, tokens_entrada, tokens_salida).
# Escribe tu adaptador al proveedor que uses y deja esta firma para poder probar con un falso en los tests.
LLMClient = Callable[[str], tuple[str, int, int]]


@dataclass
class Resultado:
    tema: str | None
    confianza: str | None
    ok: bool
    intentos: int
    tokens_entrada: int
    tokens_salida: int
    error: str | None = None


def build_prompt(texto: str) -> str:
    return (
        "Clasifica el ticket de atención al cliente en uno de estos temas: "
        f"{', '.join(TEMAS)}. Responde solo con un objeto JSON con las claves "
        '"tema" y "confianza" (alta, media o baja). Si ninguno encaja, usa "otro".\n'
        f"Ticket: {texto}"
    )


def parse_and_validate(respuesta: str) -> tuple[dict | None, str | None]:
    """(datos, error). Tolera vallas de código y texto alrededor; valida claves y valores (sin distinguir mayúsculas)."""
    # TODO
    raise NotImplementedError


def classify_text(client: LLMClient, texto: str, max_reintentos: int = 1) -> Resultado:
    """Pide la clasificación, valida y reintenta (con el error en el prompt) hasta max_reintentos veces.

    Suma los tokens de TODAS las llamadas. Si no hay respuesta válida, devuelve ok=False con el error.
    """
    # TODO
    raise NotImplementedError


def cost_eur(tokens_in: int, tokens_out: int, price_in_per_m: float, price_out_per_m: float) -> float:
    """Coste en euros; los precios son por millón de tokens."""
    # TODO
    raise NotImplementedError


__all__ = ["CONFIANZAS", "TEMAS", "Resultado", "classify_text", "cost_eur", "json", "parse_and_validate"]
