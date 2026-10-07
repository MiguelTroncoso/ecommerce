"""Linea de detalle de un pedido (composicion de Pedido)."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.producto import Producto


class DetallePedido:
    """Congela cantidad y precio unitario pactado al momento de la venta."""

    def __init__(
        self,
        producto: Producto,
        cantidad: int,
        precio_unitario_congelado: float,
        id_detalle: int | None = None,
    ) -> None:
        self._id_detalle = id_detalle
        self._producto = producto
        self._cantidad = 0
        self._precio_unitario_congelado = 0.0
        self.cantidad = cantidad
        self.precio_unitario_congelado = precio_unitario_congelado

    @property
    def id_detalle(self) -> int | None:
        return self._id_detalle

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatoInvalidoError("La cantidad de la linea debe ser un numero entero.")
        if valor <= 0:
            raise DatoInvalidoError("La cantidad de la linea debe ser mayor que cero.")
        self._cantidad = valor

    @property
    def precio_unitario_congelado(self) -> float:
        return self._precio_unitario_congelado

    @precio_unitario_congelado.setter
    def precio_unitario_congelado(self, valor: float) -> None:
        valor = float(valor)
        if valor < 0:
            raise DatoInvalidoError("El precio unitario congelado no puede ser negativo.")
        self._precio_unitario_congelado = round(valor, 2)

    def calcular_subtotal(self) -> float:
        return round(self._cantidad * self._precio_unitario_congelado, 2)

    def to_dict(self) -> dict:
        return {
            "id_producto": self._producto.id_producto,
            "cantidad": self._cantidad,
            "precio_unitario_congelado": self._precio_unitario_congelado,
            "subtotal": self.calcular_subtotal(),
        }

    def __str__(self) -> str:
        return (
            f"{self._cantidad} x {self._producto.nombre} "
            f"@ ${self._precio_unitario_congelado:,.0f} = ${self.calcular_subtotal():,.0f}"
        )
