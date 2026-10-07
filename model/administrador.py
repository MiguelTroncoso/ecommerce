"""Rol gerencial: control total del catalogo y autorizacion de despacho."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.producto import Producto
from model.trabajador import Trabajador


class Administrador(Trabajador):
    """Gestiona catalogo, precios y tambien puede autorizar despachos."""

    ROL = "ADMINISTRADOR"

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        correo: str,
        nivel_acceso: int = 1,
        password_hash: str = "",
        salt: str = "",
    ) -> None:
        super().__init__(id_trabajador, nombre, correo, password_hash, salt)
        self._nivel_acceso = 1
        self.nivel_acceso = nivel_acceso

    @property
    def nivel_acceso(self) -> int:
        return self._nivel_acceso

    @nivel_acceso.setter
    def nivel_acceso(self, valor: int) -> None:
        valor = int(valor)
        if valor not in (1, 2, 3):
            raise DatoInvalidoError("El nivel de acceso debe ser 1, 2 o 3.")
        self._nivel_acceso = valor

    def puede_modificar_catalogo(self) -> bool:
        return True

    def puede_despachar(self) -> bool:
        return True

    def actualizar_precio(self, producto: Producto, nuevo_precio_clp: float) -> None:
        if not self.puede_modificar_catalogo():
            from model.excepciones import SinPermisoError

            raise SinPermisoError("modificar precios", self.rol)
        producto.precio_base_clp = nuevo_precio_clp

    def registrar_nuevo_producto(self, producto: Producto) -> str:
        return f"Producto {producto.nombre} registrado por {self.nombre}."

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["extra"] = str(self._nivel_acceso)
        return datos
