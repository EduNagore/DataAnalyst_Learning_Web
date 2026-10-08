import math


def redondear_significativo(valor: float, cifras: int = 3) -> float:
    """Redondea a `cifras` cifras significativas (0 se devuelve tal cual)."""
    # TODO
    ...


def formatear_es(valor: float, decimales: int = 1) -> str:
    """Formato español: miles con punto y decimales con coma (1234.56 -> '1.234,6')."""
    # TODO
    ...


def en_millones(valor: float, decimales: int = 1) -> str:
    """49460756.64 -> '49,5 M€'."""
    # TODO
    ...


def describir_cambio(nombre: str, actual: float, anterior: float, tipo: str) -> str:
    """'Ingresos: +120,4 % (de 22,4 M€ a 49,5 M€)' o 'Conversión: -0,12 pp (del 4,29 % al 4,17 %)'."""
    # TODO
    ...


def rango_texto(media: float, se: float, unidad: str = "€", confianza: str = "95 %") -> str:
    """'entre 172 y 432 € (95 % de confianza)' para media ± 1,96·se."""
    # TODO
    ...


print(redondear_significativo(49460756.64), en_millones(49460756.64))
print(describir_cambio("Ingresos", 49460757, 22441854, "euros"))
print(describir_cambio("Conversión", 4.17, 4.29, "tasa"))
print(rango_texto(301.7, 66.41))
