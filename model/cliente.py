"""Entidad Cliente: identidad del comprador y validacion obligatoria."""

from __future__ import annotations

import re

from model.excepciones import DatoInvalidoError, IdentificadorInvalidoError

_PATRON_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def limpiar_rut(rut: str) -> str:
    """Deja el RUT en formato ``12345678K`` (sin puntos ni guion)."""
    return re.sub(r"[.\-\s]", "", rut).upper()


def calcular_digito_verificador(cuerpo: str) -> str:
    """Calcula el digito verificador de un RUT chileno con el modulo 11."""
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = suma % 11
    resultado = 11 - resto
    if resultado == 11:
        return "0"
    if resultado == 10:
        return "K"
    return str(resultado)


def validar_rut(rut: str) -> bool:
    """Valida un RUT chileno aplicando el algoritmo Modulo 11."""
    limpio = limpiar_rut(rut)
    if len(limpio) < 2:
        return False
    cuerpo, digito = limpio[:-1], limpio[-1]
    if not cuerpo.isdigit():
        return False
    return calcular_digito_verificador(cuerpo) == digito


def validar_email(email: str) -> bool:
    """Valida el formato sintactico de un correo electronico."""
    return bool(_PATRON_EMAIL.match(email.strip()))


class Cliente:
    """Comprador de ClickAndGo.

    El atributo ``identificador`` es el dato con validacion obligatoria que
    exige la ficha del negocio: acepta RUT chileno (Modulo 11) o correo
    electronico, y **rechaza** cualquier valor invalido lanzando
    :class:`IdentificadorInvalidoError` desde el ``setter``.
    """

    TIPOS_VALIDOS = ("RUT", "EMAIL")

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        identificador: str,
        tipo_identificador: str = "RUT",
    ) -> None:
        self._id_cliente = ""
        self._nombre = ""
        self._identificador = ""
        self._tipo_identificador = "RUT"
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.tipo_identificador = tipo_identificador
        self.identificador = identificador

    # ------------------------------------------------------------------
    # Propiedades con validacion en el setter
    # ------------------------------------------------------------------
    @property
    def id_cliente(self) -> str:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise DatoInvalidoError("El identificador interno del cliente no puede estar vacio.")
        self._id_cliente = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if len(valor) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor

    @property
    def tipo_identificador(self) -> str:
        return self._tipo_identificador

    @tipo_identificador.setter
    def tipo_identificador(self, valor: str) -> None:
        valor = str(valor).strip().upper()
        if valor not in self.TIPOS_VALIDOS:
            raise DatoInvalidoError(
                f"Tipo de identificador invalido '{valor}'. Use RUT o EMAIL."
            )
        self._tipo_identificador = valor

    @property
    def identificador(self) -> str:
        return self._identificador

    @identificador.setter
    def identificador(self, valor: str) -> None:
        valor = str(valor).strip()
        if self._tipo_identificador == "EMAIL":
            if not validar_email(valor):
                raise IdentificadorInvalidoError(
                    f"El correo '{valor}' no tiene un formato valido (ejemplo: cliente@correo.cl)."
                )
        else:
            if not validar_rut(valor):
                raise IdentificadorInvalidoError(
                    f"El RUT '{valor}' no supera la validacion Modulo 11."
                )
        self._identificador = valor

    # ------------------------------------------------------------------
    # Comportamiento
    # ------------------------------------------------------------------
    @property
    def identificador_normalizado(self) -> str:
        if self._tipo_identificador == "EMAIL":
            return self._identificador.lower()
        return limpiar_rut(self._identificador)

    def validar_identificador(self) -> bool:
        """Verifica el dato obligatorio sin lanzar excepciones."""
        if self._tipo_identificador == "EMAIL":
            return validar_email(self._identificador)
        return validar_rut(self._identificador)

    def to_dict(self) -> dict:
        return {
            "id_cliente": self._id_cliente,
            "nombre": self._nombre,
            "identificador": self._identificador,
            "tipo_identificador": self._tipo_identificador,
        }

    @classmethod
    def from_row(cls, fila) -> "Cliente":
        return cls(
            id_cliente=fila["id_cliente"],
            nombre=fila["nombre"],
            identificador=fila["identificador"],
            tipo_identificador=fila["tipo_identificador"],
        )

    def __str__(self) -> str:
        return f"{self._nombre} ({self._tipo_identificador}: {self._identificador})"
