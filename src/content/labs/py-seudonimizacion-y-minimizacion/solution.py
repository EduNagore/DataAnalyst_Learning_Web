import hashlib
import hmac

import pandas as pd
from datakit.data import load_table

clientes = load_table("customers")
CLAVE = b"clave-secreta-del-proyecto"  # en la vida real: fuera del código, en un gestor de secretos


def hash_simple(valor: str) -> str:
    """SHA-256 del texto (sin clave), en hexadecimal."""
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def seudonimo(valor: str, clave: bytes) -> str:
    """HMAC-SHA256 del texto con la clave secreta, en hexadecimal: el mismo valor y la misma clave dan siempre el
    mismo seudónimo, pero sin la clave no se puede recalcular."""
    return hmac.new(clave, valor.encode("utf-8"), hashlib.sha256).hexdigest()


def minimizar(df: pd.DataFrame, necesarias: list[str]) -> pd.DataFrame:
    """Conserva solo las columnas necesarias para el fin del análisis (minimización de datos), en ese orden."""
    return df[necesarias].copy()


def seudonimizar_tabla(df: pd.DataFrame, columna_id: str, clave: bytes) -> pd.DataFrame:
    """Sustituye la columna identificadora por la columna `seudonimo` (HMAC del identificador) y elimina el original.
    El resto de columnas no cambia y el orden de las filas se conserva."""
    out = df.copy()
    out["seudonimo"] = [seudonimo(v, clave) for v in out[columna_id]]
    return out.drop(columns=[columna_id])


def ataque_de_diccionario(objetivo: str, candidatos: list[str]):
    """Prueba cada candidato con SHA-256 sin clave y devuelve el que coincide con el hash objetivo (None si ninguno)."""
    for c in candidatos:
        if hash_simple(c) == objetivo:
            return c
    return None


def tasa_de_reidentificacion(hashes: list[str], candidatos: list[str]) -> float:
    """Porcentaje de hashes que un atacante recupera probando SHA-256 sin clave sobre todos los candidatos."""
    tabla = {hash_simple(c): c for c in candidatos}
    return float(100 * sum(h in tabla for h in hashes) / len(hashes))


ids = clientes["customer_id"].tolist()
muestra = ids[:2000]
simples = [hash_simple(i) for i in muestra]
con_clave = [seudonimo(i, CLAVE) for i in muestra]
print("hash sin clave reidentificado:", tasa_de_reidentificacion(simples, ids), "%")
print("seudónimo con clave reidentificado:", tasa_de_reidentificacion(con_clave, ids), "%")
tabla = seudonimizar_tabla(minimizar(clientes, ["customer_id", "segment", "region"]), "customer_id", CLAVE)
print(list(tabla.columns), len(tabla))
