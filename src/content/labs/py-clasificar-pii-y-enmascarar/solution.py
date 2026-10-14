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
    m = re.fullmatch(r"(\d{8})([A-Z])", str(valor).strip().upper())
    return bool(m) and LETRAS_DNI[int(m.group(1)) % 23] == m.group(2)


def es_email(valor: str) -> bool:
    """Dirección de correo con la forma texto@dominio.extensión (sin espacios)."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", str(valor).strip()))


def es_iban_es(valor: str) -> bool:
    """IBAN español válido: «ES» + 22 dígitos y control módulo 97 (se mueven los 4 primeros caracteres al final,
    se sustituye cada letra por su valor A=10…Z=35 y el número resultante módulo 97 debe ser 1)."""
    v = str(valor).replace(" ", "").upper()
    if not re.fullmatch(r"ES\d{22}", v):
        return False
    reordenado = v[4:] + v[:4]
    numero = "".join(str(int(c, 36)) for c in reordenado)
    return int(numero) % 97 == 1


def clasificar_columna(serie: pd.Series) -> str:
    """Devuelve «identificador_directo» si al menos el 80 % de los valores no nulos son DNI válidos, correos o IBAN
    españoles válidos, o si la columna se llama «nombre», «apellidos», «name» o «telefono»; «cuasi_identificador» si el
    nombre contiene «region», «provincia»/«province», «fecha»/«date» o es «cp»; «identificador_indirecto» si se llama
    «*_id» o «id»; y «ninguno» en otro caso."""
    valores = serie.dropna().astype(str)
    if len(valores) and max(
        valores.map(es_dni).mean(), valores.map(es_email).mean(), valores.map(es_iban_es).mean()
    ) >= 0.8:
        return "identificador_directo"
    nombre = str(serie.name).lower()
    if nombre in ("nombre", "apellidos", "name", "telefono"):
        return "identificador_directo"
    if any(p in nombre for p in ("region", "provincia", "province", "fecha", "date")) or nombre == "cp":
        return "cuasi_identificador"
    if nombre == "id" or nombre.endswith("_id"):
        return "identificador_indirecto"
    return "ninguno"


def enmascarar(valor: str, tipo: str) -> str:
    """Enmascara un valor: «email» → primera letra + *** + @dominio; «dni» → cuatro asteriscos y los 4 últimos caracteres («****678Z»); «iban» → «ES**» + asteriscos hasta los 4 últimos dígitos (misma longitud).
    Otro tipo → ValueError."""
    v = str(valor)
    if tipo == "email":
        local, _, dominio = v.partition("@")
        return local[0] + "***@" + dominio
    if tipo == "dni":
        return "****" + v[-4:]
    if tipo == "iban":
        return v[:2] + "**" + "*" * (len(v) - 8) + v[-4:]
    raise ValueError(f"Tipo desconocido: {tipo}")


def politica_de_acceso(clasificacion: dict[str, str], rol: str) -> dict[str, str]:
    """Qué ve cada rol de cada columna: «ver», «enmascarar» o «ocultar».
    - «soporte»: ve todo salvo identificadores directos, que ve enmascarados.
    - «analista»: oculta los identificadores directos, ve enmascarados los indirectos y el resto tal cual.
    - «finanzas»: ve todo en claro.
    Rol desconocido → ValueError."""
    if rol not in ("finanzas", "soporte", "analista"):
        raise ValueError(f"Rol desconocido: {rol}")
    politica = {}
    for col, clase in clasificacion.items():
        if rol == "finanzas":
            politica[col] = "ver"
        elif rol == "soporte":
            politica[col] = "enmascarar" if clase == "identificador_directo" else "ver"
        else:
            politica[col] = {"identificador_directo": "ocultar", "identificador_indirecto": "enmascarar"}.get(clase, "ver")
    return politica


clasificacion = {c: clasificar_columna(soporte[c]) for c in soporte.columns}
print(clasificacion)
print({c: clasificar_columna(load_table("customers")[c]) for c in load_table("customers").columns})
print(politica_de_acceso(clasificacion, "analista"))
