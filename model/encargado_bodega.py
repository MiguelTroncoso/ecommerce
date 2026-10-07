"""Rol operativo: prepara y despacha, sin acceso al catalogo."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.trabajador import Trabajador


class EncargadoBodega(Trabajador):
    """Puede despachar pedidos, pero no modificar precios ni catalogo."""

    ROL = "ENCARGADO_BODEGA"

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        correo: str,
        zona_bodega: str = "Zona A",
        password_hash: str = "",
        salt: str = "",
    ) -> None:
        super().__init__(id_trabajador, nombre, correo, password_hash, salt)
        self._zona_bodega = ""
        self.zona_bodega = zona_bodega

    @property
    def zona_bodega(self) -> str:
        return self._zona_bodega

    @zona_bodega.setter
    def zona_bodega(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise DatoInvalidoError("La zona de bodega no puede estar vacia.")
        self._zona_bodega = valor

    def puede_modificar_catalogo(self) -> bool:
        return False

    def puede_despachar(self) -> bool:
        return True

    def registrar_preparacion(self, pedido) -> str:
        return (
            f"Pedido {pedido.id_pedido} preparado por {self.nombre} "
            f"en {self._zona_bodega}."
        )

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["extra"] = self._zona_bodega
        return datos
