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
    # TODO
    ...


def contraste(hex1: str, hex2: str) -> float:
    """Relación de contraste WCAG entre dos colores (2 decimales)."""
    # TODO
    ...


def cumple_wcag(fg: str, bg: str, uso: str) -> bool:
    """True si el contraste alcanza 4,5 (uso='texto') o 3 (uso='grafico')."""
    # TODO
    ...


def fuera_de_banda(p: float, n: int, observado: float) -> bool:
    """True si `observado` (%) queda fuera de p ± 1,96·sqrt(p(1-p)/n), con p en %."""
    # TODO
    ...


for nombre, h in OKABE_ITO.items():
    print(nombre, h, contraste(h, BLANCO), contraste(h, FONDO_OSCURO), cumple_wcag(h, BLANCO, "grafico"))
print(fuera_de_banda(4.24, 707, 2.66), fuera_de_banda(4.24, 707, 4.0))
