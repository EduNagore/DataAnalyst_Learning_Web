import re
from collections import Counter

REF = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)")


def _col_a_numero(letras: str) -> int:
    return sum((ord(c) - 64) * 26**i for i, c in enumerate(reversed(letras)))


def _separar(celda: str) -> tuple[int, int]:
    m = REF.fullmatch(celda)
    return int(m.group(4)), _col_a_numero(m.group(2))


def a_r1c1(formula: str, celda: str) -> str:
    """Convierte las referencias A1 de `formula` (escrita en `celda`) a notación R1C1."""
    fila0, col0 = _separar(celda)

    def cambiar(m: re.Match) -> str:
        abs_col, letras, abs_fila, fila = m.groups()
        fila, col = int(fila), _col_a_numero(letras)
        r = f"R{fila}" if abs_fila else f"R[{fila - fila0}]"
        c = f"C{col}" if abs_col else f"C[{col - col0}]"
        return r + c

    return REF.sub(cambiar, formula)


def celdas_inconsistentes(serie: dict[str, object]) -> list[str]:
    """Celdas cuya fórmula rompe el patrón mayoritario o que no son fórmulas."""
    patrones = {
        celda: a_r1c1(v, celda) if isinstance(v, str) and v.startswith("=") else None
        for celda, v in serie.items()
    }
    comunes = Counter(p for p in patrones.values() if p is not None).most_common(1)
    mayoritario = comunes[0][0] if comunes else None
    return [celda for celda, p in patrones.items() if p is None or p != mayoritario]


_SUMA = re.compile(r"SUM[A]?\(\s*\$?([A-Z]{1,3})\$?(\d+)\s*:\s*\$?([A-Z]{1,3})\$?(\d+)\s*\)")


def suma_incompleta(formula: str, ultima_celda: str) -> bool:
    """True si una suma termina antes de `ultima_celda` en su misma fila o columna."""
    m = _SUMA.search(formula.upper())
    if not m:
        return False
    fila_ult, col_ult = _separar(ultima_celda)
    fila_fin, col_fin = int(m.group(4)), _col_a_numero(m.group(3))
    fila_ini, col_ini = int(m.group(2)), _col_a_numero(m.group(1))
    if fila_ini == fila_fin == fila_ult:
        return col_fin < col_ult
    if col_ini == col_fin == col_ult:
        return fila_fin < fila_ult
    return False


def numeros_como_texto(valores: dict[str, object]) -> list[str]:
    """Celdas con un `str` que representa un número."""
    out = []
    for celda, v in valores.items():
        if not isinstance(v, str):
            continue
        t = v.strip().replace(" ", "")
        if re.fullmatch(r"[-+]?\d{1,3}(\.\d{3})+(,\d+)?|[-+]?\d+([.,]\d+)?", t):
            out.append(celda)
    return out


fila_8 = {f"{c}8": f"={c}7*Supuestos!$B$2" for c in "BCDE"}
fila_8["F8"] = "=F7*Supuestos!F2"  # referencia sin anclar
fila_8["G8"] = 4120.5  # valor pegado
print(a_r1c1("=F7*Supuestos!$B$2", "F8"))
print(celdas_inconsistentes(fila_8))
print(suma_incompleta("=SUM(B9:L9)", "M9"))
print(numeros_como_texto({"D5": "1.250", "E5": 1250, "F5": "n/a"}))
