"""Entrada segura de datos: toda entrada del usuario se valida antes de usarse.

Ninguna funcion de este modulo deja caer el programa: ante un dato invalido
informa el problema y vuelve a solicitarlo.
"""

from __future__ import annotations

from datetime import datetime

from model.excepciones import DatoInvalidoError
from model.cliente import validar_email, validar_rut


def limpiar_texto(valor: str) -> str:
    return " ".join(str(valor).split())


def validar_texto(valor: str, minimo: int = 3, maximo: int = 80) -> str:
    limpio = limpiar_texto(valor)
    if len(limpio) < minimo:
        raise DatoInvalidoError(f"Debe ingresar al menos {minimo} caracteres.")
    if len(limpio) > maximo:
        raise DatoInvalidoError(f"El texto no puede superar los {maximo} caracteres.")
    return limpio


def validar_entero(valor, minimo: int | None = None, maximo: int | None = None) -> int:
    if isinstance(valor, bool):
        raise DatoInvalidoError("Se esperaba un numero entero.")
    if isinstance(valor, int):
        numero = valor
    else:
        texto = str(valor).strip().replace(" ", "")
        if not texto or not texto.lstrip("+-").isdigit():
            raise DatoInvalidoError(f"'{valor}' no es un numero entero valido.")
        numero = int(texto)
    if minimo is not None and numero < minimo:
        raise DatoInvalidoError(f"El valor debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        raise DatoInvalidoError(f"El valor debe ser menor o igual a {maximo}.")
    return numero


def validar_decimal(valor, minimo: float | None = None, maximo: float | None = None) -> float:
    if isinstance(valor, bool):
        raise DatoInvalidoError("Se esperaba un numero decimal.")
    texto = str(valor).strip().replace(" ", "")
    texto = texto.replace("$", "").replace("USD", "").replace("usd", "")
    if "," in texto and "." in texto:
        texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        numero = float(texto)
    except (TypeError, ValueError) as error:
        raise DatoInvalidoError(f"'{valor}' no es un numero decimal valido.") from error
    if minimo is not None and numero < minimo:
        raise DatoInvalidoError(f"El valor debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        raise DatoInvalidoError(f"El valor debe ser menor o igual a {maximo}.")
    return round(numero, 2)


def validar_identificador(valor: str, tipo: str) -> str:
    """Valida el dato obligatorio de la ficha: RUT chileno o correo."""
    valor = str(valor).strip()
    if tipo.upper() == "EMAIL":
        if not validar_email(valor):
            raise DatoInvalidoError(
                f"El correo '{valor}' no es valido. Formato esperado: cliente@correo.cl"
            )
    else:
        if not validar_rut(valor):
            raise DatoInvalidoError(
                f"El RUT '{valor}' no es valido (debe cumplir el algoritmo Modulo 11)."
            )
    return valor


def validar_fecha_futura(texto: str) -> datetime:
    try:
        fecha = datetime.strptime(str(texto).strip(), "%Y-%m-%d %H:%M")
    except ValueError as error:
        raise DatoInvalidoError(
            "Formato de fecha invalido. Use AAAA-MM-DD HH:MM (ejemplo: 2026-11-20 15:30)."
        ) from error
    if fecha <= datetime.now():
        raise DatoInvalidoError("La fecha debe ser futura para poder agendar el servicio.")
    return fecha


def validar_url(texto: str) -> str:
    texto = str(texto).strip()
    if not texto.startswith(("http://", "https://")):
        raise DatoInvalidoError("La URL debe comenzar con http:// o https://")
    return texto


def leer(entrada, mensaje: str) -> str:
    """Solicita un texto. ``entrada`` permite inyectar otro origen (pruebas)."""
    return limpiar_texto(entrada(mensaje))


# ----------------------------------------------------------------------
# Lectores interactivos con reintento (usados por main.py)
# ----------------------------------------------------------------------
def pedir_texto(mensaje, leer_entrada=input, minimo=3, maximo=80, permitir_vacio=False) -> str:
    while True:
        try:
            valor = limpiar_texto(leer_entrada(f"{mensaje}: "))
            if permitir_vacio and not valor:
                return ""
            return validar_texto(valor, minimo, maximo)
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_entero(mensaje, leer_entrada=input, minimo=None, maximo=None) -> int:
    while True:
        try:
            return validar_entero(leer_entrada(f"{mensaje}: "), minimo, maximo)
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_decimal(mensaje, leer_entrada=input, minimo=None, maximo=None) -> float:
    while True:
        try:
            return validar_decimal(leer_entrada(f"{mensaje}: "), minimo, maximo)
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_fecha_futura(mensaje, leer_entrada=input) -> datetime:
    while True:
        try:
            return validar_fecha_futura(leer_entrada(f"{mensaje}: "))
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_identificador(mensaje, tipo, leer_entrada=input) -> str:
    while True:
        try:
            return validar_identificador(leer_entrada(f"{mensaje}: "), tipo)
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_url(mensaje, leer_entrada=input) -> str:
    while True:
        try:
            return validar_url(leer_entrada(f"{mensaje}: "))
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")


def pedir_opcion(mensaje, opciones_validas, leer_entrada=input):
    """Lee una opcion de menu. Acepta texto porque el test P18 envia '99'."""
    while True:
        respuesta = limpiar_texto(leer_entrada(f"{mensaje}: "))
        if respuesta.lower() in {str(o).lower() for o in opciones_validas}:
            return respuesta
        print(f"  [!] Opcion '{respuesta}' no existe. Opciones validas: {', '.join(map(str, opciones_validas))}.")
        return None
