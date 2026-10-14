import re

import pandas as pd
from datakit.data import load_table

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

# Muestra SINTÉTICA de un export de soporte (ningún dato es real)
soporte = pd.DataFrame(
    {
        "ticket": ["t1", "t2", "t3", "t4"],
        "nombre": ["Ana Pérez", "Luis Gómez", "Marta Ruiz", "Pablo Sanz"],
        "email": ["ana.perez@correo.es", "luis@ejemplo.com", "marta.ruiz@correo.es", "pablo@ejemplo.com"],
        "dni": ["12345678Z", "00000000T", "87654321X", "11111111H"],
        "iban": ["ES9121000418450200051332", "ES7921000813610123456789", "ES6621000418401234567891", "ES9121000418450200051332"],
        "region": ["Madrid", "Cataluña", "Andalucía", "Madrid"],
        "texto": ["No me llega el pedido", "Quiero devolver", "Cobro duplicado", "Cambio de dirección"],
    }
)


def es_dni(valor: str) -> bool:
    """DNI español válido: 8 dígitos y la letra de control = LETRAS_DNI[número % 23]."""
    # TODO
    ...


def es_email(valor: str) -> bool:
    """Dirección de correo con la forma texto@dominio.extensión (sin espacios)."""
    # TODO
    ...


def es_iban_es(valor: str) -> bool:
    """IBAN español válido: «ES» + 22 dígitos y control módulo 97 (se mueven los 4 primeros caracteres al final,
    se sustituye cada letra por su valor A=10…Z=35 y el número resultante módulo 97 debe ser 1)."""
    # TODO
    ...


def clasificar_columna(serie: pd.Series) -> str:
    """Devuelve «identificador_directo» si al menos el 80 % de los valores no nulos son DNI válidos, correos o IBAN
    españoles válidos, o si la columna se llama «nombre», «apellidos», «name» o «telefono»; «cuasi_identificador» si el
    nombre contiene «region», «provincia»/«province», «fecha»/«date» o es «cp»; «identificador_indirecto» si se llama
    «*_id» o «id»; y «ninguno» en otro caso."""
    # TODO
    ...


def enmascarar(valor: str, tipo: str) -> str:
    """Enmascara un valor: «email» → primera letra + *** + @dominio; «dni» → cuatro asteriscos y los 4 últimos caracteres («****678Z»); «iban» → «ES**» + asteriscos hasta los 4 últimos dígitos (misma longitud).
    Otro tipo → ValueError."""
    # TODO
    ...


def politica_de_acceso(clasificacion: dict[str, str], rol: str) -> dict[str, str]:
    """Qué ve cada rol de cada columna: «ver», «enmascarar» o «ocultar».
    - «soporte»: ve todo salvo identificadores directos, que ve enmascarados.
    - «analista»: oculta los identificadores directos, ve enmascarados los indirectos y el resto tal cual.
    - «finanzas»: ve todo en claro.
    Rol desconocido → ValueError."""
    # TODO
    ...


clasificacion = {c: clasificar_columna(soporte[c]) for c in soporte.columns}
print(clasificacion)
print({c: clasificar_columna(load_table("customers")[c]) for c in load_table("customers").columns})
print(politica_de_acceso(clasificacion, "analista"))
