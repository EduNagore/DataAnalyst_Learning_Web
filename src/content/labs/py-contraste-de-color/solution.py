import math

OKABE_ITO = {
    "naranja": "#E69F00",
    "azul cielo": "#56B4E9",
    "verde azulado": "#009E73",
    "amarillo": "#F0E442",
    "azul": "#0072B2",
    "bermellón": "#D55E00",
    "púrpura rojizo": "#CC79A7",
    "negro": "#000000",
}
BLANCO = "#FFFFFF"
FONDO_OSCURO = "#0B1220"


def luminancia(hex_color: str) -> float:
    """Luminancia relativa de un color #RRGGBB (6 decimales)."""
    h = hex_color.lstrip("#")
    canales = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return round(0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2], 6)


def contraste(hex1: str, hex2: str) -> float:
    """Relación de contraste WCAG entre dos colores (2 decimales)."""
    a, b = luminancia(hex1), luminancia(hex2)
    claro, oscuro = max(a, b), min(a, b)
    return round((claro + 0.05) / (oscuro + 0.05), 2)


def cumple_wcag(fg: str, bg: str, uso: str) -> bool:
    """True si el contraste alcanza 4,5 (uso='texto') o 3 (uso='grafico')."""
    umbral = {"texto": 4.5, "grafico": 3.0}.get(uso)
    if umbral is None:
        raise ValueError(f"Uso no reconocido: {uso!r} (usa 'texto' o 'grafico')")
    return contraste(fg, bg) >= umbral


def fuera_de_banda(p: float, n: int, observado: float) -> bool:
    """True si `observado` (%) queda fuera de p ± 1,96·sqrt(p(1-p)/n), con p en %."""
    q = p / 100
    ruido = 1.96 * math.sqrt(q * (1 - q) / n) * 100
    return observado < p - ruido or observado > p + ruido


for nombre, h in OKABE_ITO.items():
    print(nombre, h, contraste(h, BLANCO), contraste(h, FONDO_OSCURO), cumple_wcag(h, BLANCO, "grafico"))
print(fuera_de_banda(4.24, 707, 2.66), fuera_de_banda(4.24, 707, 4.0))
