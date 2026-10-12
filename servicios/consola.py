"""Utilidades de presentacion para la consola.

Centraliza el formato de la interfaz: titulos, paneles, tablas, mensajes de
estado y color. El color se activa solo cuando la salida es una terminal
interactiva, de modo que las pruebas automatizadas y los archivos de registro
reciben texto plano.
"""

from __future__ import annotations

import os
import sys

ANCHO = 78

_RESET = "\033[0m"
_NEGRITA = "\033[1m"
_ROJO = "\033[31m"
_VERDE = "\033[32m"
_AMARILLO = "\033[33m"
_CIAN = "\033[36m"
_GRIS = "\033[90m"

_color_activo: bool | None = None


def habilitar_color(valor: bool | None = None) -> bool:
    """Activa o desactiva el color. ``None`` lo detecta automaticamente."""
    global _color_activo
    if valor is None:
        variable = os.environ.get("CLICKANDGO_COLOR", "").strip().lower()
        if variable in ("0", "false", "no", "off"):
            valor = False
        elif variable in ("1", "true", "si", "on"):
            valor = True
        else:
            valor = bool(getattr(sys.stdout, "isatty", lambda: False)()) and (
                os.environ.get("TERM", "") != "dumb"
            )
    _color_activo = bool(valor)
    return _color_activo


def _pintar(texto: str, codigo: str) -> str:
    if _color_activo is None:
        habilitar_color()
    if not _color_activo:
        return texto
    return f"{codigo}{texto}{_RESET}"


def azul(texto: str) -> str:
    return _pintar(texto, _CIAN)


def verde(texto: str) -> str:
    return _pintar(texto, _VERDE)


def rojo(texto: str) -> str:
    return _pintar(texto, _ROJO)


def ambar(texto: str) -> str:
    return _pintar(texto, _AMARILLO)


def gris(texto: str) -> str:
    return _pintar(texto, _GRIS)


def negrita(texto: str) -> str:
    return _pintar(texto, _NEGRITA)


# ----------------------------------------------------------------------
# Estructura de la pantalla
# ----------------------------------------------------------------------
def linea(caracter: str = "-") -> str:
    return caracter * ANCHO


def titulo(texto: str) -> None:
    barra = "=" * ANCHO
    print(f"\n{barra}")
    print(f"  {negrita(texto)}")
    print(barra)


def subtitulo(texto: str) -> None:
    print(f"\n{linea('-')}")
    print(f"  {azul(texto)}")
    print(linea("-"))


def panel(titulo_panel: str, filas: list[tuple[str, str]]) -> None:
    """Panel de resumen con etiqueta y valor alineados."""
    ancho_etiqueta = max((len(etiqueta) for etiqueta, _ in filas), default=0)
    print("\n  +" + "-" * (ANCHO - 4) + "+")
    print(f"  | {negrita(titulo_panel.ljust(ANCHO - 5))}|")
    print("  +" + "-" * (ANCHO - 4) + "+")
    for etiqueta, valor in filas:
        texto = f"{etiqueta.ljust(ancho_etiqueta)} : {valor}"
        print(f"  | {texto[: ANCHO - 5].ljust(ANCHO - 5)}|")
    print("  +" + "-" * (ANCHO - 4) + "+")


def paso(numero: int, total: int, texto: str) -> str:
    """Etiqueta del tipo [2/4] para guiar formularios largos."""
    return f"[{numero}/{total}] {texto}"


def ok(texto: str) -> None:
    print(f"\n  {verde('[OK]')} {texto}")


def aviso(texto: str) -> None:
    print(f"  {ambar('[!]')} {texto}")


def info(texto: str) -> None:
    print(f"  {azul('[i]')} {texto}")


def error(texto: str) -> None:
    print(f"  {rojo('[X]')} {texto}")


def tabla(
    encabezados: list[str],
    filas: list[list[str]],
    alineaciones: list[str] | None = None,
    sangria: str = "  ",
) -> None:
    """Tabla de texto con columnas alineadas automaticamente."""
    if not filas:
        return
    total_columnas = len(encabezados)
    alineaciones = alineaciones or ["<"] * total_columnas
    anchos = [len(str(encabezado)) for encabezado in encabezados]
    for fila in filas:
        for indice in range(total_columnas):
            celda = str(fila[indice]) if indice < len(fila) else ""
            anchos[indice] = max(anchos[indice], len(celda))

    # La suma de columnas no debe superar el ancho de la pantalla.
    disponible = ANCHO - len(sangria) - 2 * (total_columnas - 1)
    while sum(anchos) > disponible:
        indice_mayor = max(range(total_columnas), key=lambda i: anchos[i])
        if anchos[indice_mayor] <= 10:
            break
        anchos[indice_mayor] -= 1

    def formatear(valor: str, indice: int) -> str:
        texto = str(valor)
        if len(texto) > anchos[indice]:
            texto = texto[: max(anchos[indice] - 1, 1)] + "."
        return texto.ljust(anchos[indice]) if alineaciones[indice] == "<" else texto.rjust(anchos[indice])

    encabezado = "  ".join(formatear(valor, i) for i, valor in enumerate(encabezados))
    print(sangria + negrita(encabezado))
    print(sangria + gris("  ".join("-" * ancho for ancho in anchos)))
    for fila in filas:
        print(sangria + "  ".join(formatear(fila[i] if i < len(fila) else "", i)
                                  for i in range(total_columnas)))


def listar_opciones(items: list, formatear) -> None:
    """Numeracion de una lista para elegir por numero."""
    ancho_numero = len(str(len(items)))
    for indice, item in enumerate(items, 1):
        print(f"  {str(indice).rjust(ancho_numero)}. {formatear(item)}")
