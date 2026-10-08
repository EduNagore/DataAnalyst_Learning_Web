import math


def redondear_significativo(valor: float, cifras: int = 3) -> float:
    """Redondea a `cifras` cifras significativas (0 se devuelve tal cual)."""
    if valor == 0:
        return 0
    return round(valor, cifras - 1 - math.floor(math.log10(abs(valor))))


def formatear_es(valor: float, decimales: int = 1) -> str:
    """Formato español: miles con punto y decimales con coma (1234.56 -> '1.234,6')."""
    en = f"{valor:,.{decimales}f}"
    return en.replace(",", "§").replace(".", ",").replace("§", ".")


def en_millones(valor: float, decimales: int = 1) -> str:
    """49460756.64 -> '49,5 M€'."""
    return f"{formatear_es(valor / 1e6, decimales)} M€"


def _euros(valor: float) -> str:
    return en_millones(valor) if abs(valor) >= 1_000_000 else f"{formatear_es(valor, 0)} €"


def describir_cambio(nombre: str, actual: float, anterior: float, tipo: str) -> str:
    """'Ingresos: +120,4 % (de 22,4 M€ a 49,5 M€)' o 'Conversión: -0,12 pp (del 4,29 % al 4,17 %)'."""
    if tipo == "tasa":
        dif = round(actual - anterior, 2)
        signo = "+" if dif > 0 else ""
        return (
            f"{nombre}: {signo}{formatear_es(dif, 2)} pp "
            f"(del {formatear_es(anterior, 2)} % al {formatear_es(actual, 2)} %)"
        )
    if tipo == "euros":
        rel = round((actual - anterior) / anterior * 100, 1)
        signo = "+" if rel > 0 else ""
        return f"{nombre}: {signo}{formatear_es(rel, 1)} % (de {_euros(anterior)} a {_euros(actual)})"
    raise ValueError(f"tipo no reconocido: {tipo!r}")


def rango_texto(media: float, se: float, unidad: str = "€", confianza: str = "95 %") -> str:
    """'entre 172 y 432 € (95 % de confianza)' para media ± 1,96·se."""
    lo, hi = media - 1.96 * se, media + 1.96 * se
    return f"entre {formatear_es(lo, 0)} y {formatear_es(hi, 0)} {unidad} ({confianza} de confianza)"


print(redondear_significativo(49460756.64), en_millones(49460756.64))
print(describir_cambio("Ingresos", 49460757, 22441854, "euros"))
print(describir_cambio("Conversión", 4.17, 4.29, "tasa"))
print(rango_texto(301.7, 66.41))
