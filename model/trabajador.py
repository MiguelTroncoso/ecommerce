"""Clase base abstracta del personal: control de acceso basado en roles."""

from __future__ import annotations

import hashlib
import hmac
import os
from abc import ABC, abstractmethod

from model.excepciones import DatoInvalidoError

ITERACIONES_PBKDF2 = 120_000


class Trabajador(ABC):
    """Empleado de ClickAndGo con credenciales y permisos (RBAC)."""

    ROL = "TRABAJADOR"

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        correo: str,
        password_hash: str = "",
        salt: str = "",
    ) -> None:
        self._id_trabajador = ""
        self._nombre = ""
        self._correo = ""
        self._password_hash = ""
        self._salt = ""
        self.id_trabajador = id_trabajador
        self.nombre = nombre
        self.correo = correo
        self._password_hash = password_hash
        self._salt = salt

    # ------------------------------------------------------------------
    # Propiedades con validacion
    # ------------------------------------------------------------------
    @property
    def id_trabajador(self) -> str:
        return self._id_trabajador

    @id_trabajador.setter
    def id_trabajador(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise DatoInvalidoError("El identificador del trabajador no puede estar vacio.")
        self._id_trabajador = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if len(valor) < 3:
            raise DatoInvalidoError("El nombre del trabajador debe tener al menos 3 caracteres.")
        self._nombre = valor

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        from model.cliente import validar_email

        valor = str(valor).strip()
        if not validar_email(valor):
            raise DatoInvalidoError(f"El correo corporativo '{valor}' no es valido.")
        self._correo = valor

    @property
    def rol(self) -> str:
        return self.ROL

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def salt(self) -> str:
        return self._salt

    # ------------------------------------------------------------------
    # Autenticacion
    # ------------------------------------------------------------------
    def definir_password(self, password: str) -> None:
        """Guarda la contrasena con PBKDF2-HMAC-SHA256 y salt aleatorio."""
        if len(str(password)) < 8:
            raise DatoInvalidoError("La contrasena debe tener al menos 8 caracteres.")
        self._salt = os.urandom(16).hex()
        self._password_hash = self._calcular_hash(password, self._salt)

    def _calcular_hash(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", str(password).encode("utf-8"), bytes.fromhex(salt), ITERACIONES_PBKDF2
        ).hex()

    def verificar_password(self, password: str) -> bool:
        if not self._password_hash or not self._salt:
            return False
        calculado = self._calcular_hash(password, self._salt)
        return hmac.compare_digest(calculado, self._password_hash)

    # ------------------------------------------------------------------
    # Permisos (polimorfismo del personal)
    # ------------------------------------------------------------------
    @abstractmethod
    def puede_modificar_catalogo(self) -> bool:
        """Determina si el rol puede crear, modificar o eliminar productos."""

    @abstractmethod
    def puede_despachar(self) -> bool:
        """Determina si el rol puede marcar pedidos como despachados."""

    def to_dict(self) -> dict:
        return {
            "id_trabajador": self._id_trabajador,
            "nombre": self._nombre,
            "correo": self._correo,
            "rol": self.ROL,
            "password_hash": self._password_hash,
            "salt": self._salt,
        }

    def __str__(self) -> str:
        return f"{self._nombre} ({self.ROL})"
