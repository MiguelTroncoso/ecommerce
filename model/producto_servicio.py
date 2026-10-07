"""Servicio tecnico: se agenda para una fecha futura, sin despacho."""

from __future__ import annotations

from datetime import datetime

from model.excepciones import DatoInvalidoError
from model.producto import Producto

FORMATO_FECHA = "%Y-%m-%d %H:%M"


class ProductoServicio(Producto):
    """Prestacion profesional agendada en terreno."""

    TIPO = "SERVICIO"

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio_base_clp: float,
        stock: int,
        fecha_agendada: datetime,
        direccion_visita: str,
        duracion_estimada_horas: int,
    ) -> None:
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._fecha_agendada = datetime.now()
        self._direccion_visita = ""
        self._duracion_estimada_horas = 1
        self.fecha_agendada = fecha_agendada
        self.direccion_visita = direccion_visita
        self.duracion_estimada_horas = duracion_estimada_horas

    @property
    def fecha_agendada(self) -> datetime:
        return self._fecha_agendada

    @fecha_agendada.setter
    def fecha_agendada(self, valor: datetime) -> None:
        if isinstance(valor, str):
            try:
                valor = datetime.strptime(valor, FORMATO_FECHA)
            except ValueError as error:
                raise DatoInvalidoError(
                    "La fecha debe tener el formato AAAA-MM-DD HH:MM."
                ) from error
        if not isinstance(valor, datetime):
            raise DatoInvalidoError("La fecha de agenda no es valida.")
        if valor <= datetime.now():
            raise DatoInvalidoError("El servicio debe agendarse para una fecha futura.")
        self._fecha_agendada = valor

    @property
    def direccion_visita(self) -> str:
        return self._direccion_visita

    @direccion_visita.setter
    def direccion_visita(self, valor: str) -> None:
        valor = str(valor).strip()
        if len(valor) < 5:
            raise DatoInvalidoError("La direccion de la visita debe tener al menos 5 caracteres.")
        self._direccion_visita = valor

    @property
    def duracion_estimada_horas(self) -> int:
        return self._duracion_estimada_horas

    @duracion_estimada_horas.setter
    def duracion_estimada_horas(self, valor: int) -> None:
        valor = int(valor)
        if valor <= 0 or valor > 24:
            raise DatoInvalidoError("La duracion estimada debe estar entre 1 y 24 horas.")
        self._duracion_estimada_horas = valor

    def agendar_fecha(self, fecha: datetime) -> None:
        self.fecha_agendada = fecha

    def procesar_entrega(self, detalle) -> dict:
        return {
            "tipo": "SERVICIO_TECNICO",
            "producto": self.nombre,
            "cantidad": detalle.cantidad,
            "flete_calculado": 0.0,
            "agenda": self._fecha_agendada.strftime(FORMATO_FECHA),
            "direccion": self._direccion_visita,
            "hereda_de": "ProductoServicio",
            "mensaje": (
                f"Servicio agendado para el {self._fecha_agendada.strftime('%d/%m/%Y a las %H:%M')} hrs "
                f"en {self._direccion_visita} ({self._duracion_estimada_horas} h aprox.)."
            ),
        }

    def calcular_precio_final(self, valor_dolar: float | None = None) -> float:
        return self._precio_base_clp

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update(
            {
                "fecha_agendada": self._fecha_agendada.strftime(FORMATO_FECHA),
                "direccion_visita": self._direccion_visita,
                "duracion_estimada_horas": self._duracion_estimada_horas,
            }
        )
        return datos
