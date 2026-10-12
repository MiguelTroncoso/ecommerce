"""Generacion automatica de codigos legibles.

El usuario nunca escribe el identificador de un cliente o de un producto: el
sistema lo calcula consultando el ultimo codigo usado en la base de datos.

Formato:

    C01, C02, ...   clientes
    F01, F02, ...   productos fisicos
    D01, D02, ...   productos digitales
    S01, S02, ...   servicios
    E01, E02, ...   electronica importada
    PED-1001, ...   pedidos
"""

from __future__ import annotations

import re

from dao.conexion import ConexionBD
from model.excepciones import DatoInvalidoError

PREFIJO_CLIENTE = "C"
PREFIJO_PEDIDO = "PED-"
PRIMER_PEDIDO = 1000

PREFIJOS_PRODUCTO = {
    "FISICO": "F",
    "DIGITAL": "D",
    "SERVICIO": "S",
    "ELECTRONICA": "E",
}

# Solo estos pares tabla/columna pueden interpolarse en el SQL interno. Los
# valores son constantes del programa, nunca datos escritos por el usuario.
ORIGENES_PERMITIDOS = {
    ("clientes", "id_cliente"),
    ("productos", "id_producto"),
}


class GeneradorCodigos:
    """Calcula el siguiente codigo disponible para cada entidad."""

    def __init__(self, conexion: ConexionBD) -> None:
        self._bd = conexion

    # ------------------------------------------------------------------
    def siguiente_cliente(self) -> str:
        return self._siguiente_codigo("clientes", "id_cliente", PREFIJO_CLIENTE)

    def siguiente_producto(self, tipo: str) -> str:
        prefijo = PREFIJOS_PRODUCTO.get(str(tipo).strip().upper())
        if prefijo is None:
            raise DatoInvalidoError(
                f"No existe un prefijo de codigo para el tipo de producto '{tipo}'."
            )
        return self._siguiente_codigo("productos", "id_producto", prefijo)

    def siguiente_pedido(self) -> str:
        mayor = PRIMER_PEDIDO
        patron = re.compile(rf"^{re.escape(PREFIJO_PEDIDO)}(\d+)$")
        for fila in self._bd.consultar("SELECT id_pedido FROM pedidos"):
            coincidencia = patron.match(str(fila["id_pedido"]))
            if coincidencia:
                mayor = max(mayor, int(coincidencia.group(1)))
        return f"{PREFIJO_PEDIDO}{mayor + 1}"

    # ------------------------------------------------------------------
    def _siguiente_codigo(self, tabla: str, columna: str, prefijo: str) -> str:
        if (tabla, columna) not in ORIGENES_PERMITIDOS:
            raise DatoInvalidoError(f"Origen de codigos no permitido: {tabla}.{columna}")

        patron = re.compile(rf"^{re.escape(prefijo)}(\d+)$")
        numero = 0
        for fila in self._bd.consultar(f"SELECT {columna} AS codigo FROM {tabla}"):
            coincidencia = patron.match(str(fila["codigo"]))
            if coincidencia:
                numero = max(numero, int(coincidencia.group(1)))

        while True:
            numero += 1
            codigo = f"{prefijo}{numero:02d}"
            if not self._existe(tabla, columna, codigo):
                return codigo

    def _existe(self, tabla: str, columna: str, codigo: str) -> bool:
        fila = self._bd.consultar_uno(
            f"SELECT 1 FROM {tabla} WHERE {columna} = :codigo", {"codigo": codigo}
        )
        return fila is not None
