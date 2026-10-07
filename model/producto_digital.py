"""Producto digital: entrega inmediata por enlace, sin flete."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.producto import Producto


class ProductoDigital(Producto):
    """Bien intangible entregado al instante con enlace y licencia."""

    TIPO = "DIGITAL"

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio_base_clp: float,
        stock: int,
        enlace_descarga: str,
        licencia_activacion: str,
        peso_archivo_mb: float,
    ) -> None:
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._enlace_descarga = ""
        self._licencia_activacion = ""
        self._peso_archivo_mb = 0.0
        self.enlace_descarga = enlace_descarga
        self.licencia_activacion = licencia_activacion
        self.peso_archivo_mb = peso_archivo_mb

    @property
    def enlace_descarga(self) -> str:
        return self._enlace_descarga

    @enlace_descarga.setter
    def enlace_descarga(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor.startswith(("http://", "https://")):
            raise DatoInvalidoError("El enlace de descarga debe comenzar con http:// o https://.")
        self._enlace_descarga = valor

    @property
    def licencia_activacion(self) -> str:
        return self._licencia_activacion

    @licencia_activacion.setter
    def licencia_activacion(self, valor: str) -> None:
        valor = str(valor).strip().upper()
        if len(valor) < 4:
            raise DatoInvalidoError("La licencia de activacion debe tener al menos 4 caracteres.")
        self._licencia_activacion = valor

    @property
    def peso_archivo_mb(self) -> float:
        return self._peso_archivo_mb

    @peso_archivo_mb.setter
    def peso_archivo_mb(self, valor: float) -> None:
        valor = float(valor)
        if valor < 0:
            raise DatoInvalidoError("El peso del archivo no puede ser negativo.")
        self._peso_archivo_mb = round(valor, 2)

    def procesar_entrega(self, detalle) -> dict:
        return {
            "tipo": "DESCARGA_DIGITAL",
            "producto": self.nombre,
            "cantidad": detalle.cantidad,
            "flete_calculado": 0.0,
            "enlace": self._enlace_descarga,
            "licencia": self._licencia_activacion,
            "hereda_de": "ProductoDigital",
            "mensaje": (
                f"Entrega inmediata sin despacho (flete $0). "
                f"Enlace: {self._enlace_descarga} | Licencia: {self._licencia_activacion}."
            ),
        }

    def calcular_precio_final(self, valor_dolar: float | None = None) -> float:
        return self._precio_base_clp

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update(
            {
                "enlace_descarga": self._enlace_descarga,
                "licencia_activacion": self._licencia_activacion,
                "peso_archivo_mb": self._peso_archivo_mb,
            }
        )
        return datos
