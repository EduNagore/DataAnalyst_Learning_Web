import re
from collections import Counter

REF = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)")


def a_r1c1(formula: str, celda: str) -> str:
    """Convierte las referencias A1 de `formula` (escrita en `celda`) a notación R1C1."""
    # TODO
    ...


def celdas_inconsistentes(serie: dict[str, object]) -> list[str]:
    """Celdas cuya fórmula rompe el patrón mayoritario o que no son fórmulas."""
    # TODO
    ...


def suma_incompleta(formula: str, ultima_celda: str) -> bool:
    """True si una suma termina antes de `ultima_celda` en su misma fila o columna."""
    # TODO
    ...


def numeros_como_texto(valores: dict[str, object]) -> list[str]:
    """Celdas con un `str` que representa un número."""
    # TODO
    ...


fila_8 = {f"{c}8": f"={c}7*Supuestos!$B$2" for c in "BCDE"}
fila_8["F8"] = "=F7*Supuestos!F2"  # referencia sin anclar
fila_8["G8"] = 4120.5  # valor pegado
print(a_r1c1("=F7*Supuestos!$B$2", "F8"))
print(celdas_inconsistentes(fila_8))
print(suma_incompleta("=SUM(B9:L9)", "M9"))
print(numeros_como_texto({"D5": "1.250", "E5": 1250, "F5": "n/a"}))
