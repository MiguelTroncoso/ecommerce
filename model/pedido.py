"""Transaccion comercial: pedido compuesto por lineas de detalle."""

from __future__ import annotations

from datetime import datetime

from model.cliente import Cliente
from model.detalle_pedido import DetallePedido
from model.excepciones import (
    DatoInvalidoError,
    IdentificadorInvalidoError,
    PedidoNoPagadoError,
    PedidoVacioError,
    SinPermisoError,
    StockInsuficienteError,
)
from model.producto import Producto
from model.producto_fisico import ProductoFisico
from model.trabajador import Trabajador

ESTADOS_PAGO = ("PENDIENTE", "PAGADO", "RECHAZADO")
ESTADOS_ENTREGA = ("PENDIENTE", "EN_PREPARACION", "DESPACHADO", "ENTREGADO")


class Pedido:
    """Contrato de compraventa entre el cliente y ClickAndGo.

    Implementa las dos reglas que impiden una operacion comercial:

    * Regla 1 -> :class:`StockInsuficienteError` al confirmar sin stock.
    * Regla 2 -> :class:`PedidoNoPagadoError` al despachar sin pago.
    """

    def __init__(
        self,
        id_pedido: str,
        cliente: Cliente,
        fecha_creacion: datetime | None = None,
        estado_pago: str = "PENDIENTE",
        estado_entrega: str = "PENDIENTE",
    ) -> None:
        self._id_pedido = str(id_pedido).strip()
        if not self._id_pedido:
            raise DatoInvalidoError("El identificador del pedido no puede estar vacio.")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El pedido requiere un cliente valido.")
        self._cliente = cliente
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._estado_pago = estado_pago
        self._estado_entrega = estado_entrega
        self._total_flete_clp = 0.0
        self._total_final_clp = 0.0
        self._detalles: list[DetallePedido] = []

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------
    @property
    def id_pedido(self) -> str:
        return self._id_pedido

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def estado_pago(self) -> str:
        return self._estado_pago

    @property
    def estado_entrega(self) -> str:
        return self._estado_entrega

    @property
    def total_flete_clp(self) -> float:
        return self._total_flete_clp

    @property
    def total_final_clp(self) -> float:
        return self._total_final_clp

    @property
    def detalles(self) -> list[DetallePedido]:
        return list(self._detalles)

    # ------------------------------------------------------------------
    # Construccion de la transaccion
    # ------------------------------------------------------------------
    def agregar_linea(
        self,
        producto: Producto,
        cantidad: int,
        valor_dolar: float | None = None,
    ) -> DetallePedido:
        """Agrega una linea congelando el precio unitario vigente."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise DatoInvalidoError("La cantidad debe ser un numero entero.")
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor que cero.")
        precio = producto.calcular_precio_final(valor_dolar)
        detalle = DetallePedido(producto, cantidad, precio)
        self._detalles.append(detalle)
        self.calcular_total()
        return detalle

    def quitar_linea(self, id_producto: str) -> bool:
        for detalle in list(self._detalles):
            if detalle.producto.id_producto == id_producto:
                self._detalles.remove(detalle)
                self.calcular_total()
                return True
        return False

    # ------------------------------------------------------------------
    # Regla 1: no confirmar sin stock suficiente
    # ------------------------------------------------------------------
    def confirmar_pedido(self) -> bool:
        if not self._detalles:
            raise PedidoVacioError(
                f"El pedido {self._id_pedido} no tiene lineas de detalle."
            )
        if not self._cliente.validar_identificador():
            raise IdentificadorInvalidoError(
                f"El cliente {self._cliente.nombre} no tiene un RUT o correo valido."
            )
        for detalle in self._detalles:
            producto = detalle.producto
            if not producto.tiene_stock_suficiente(detalle.cantidad):
                raise StockInsuficienteError(
                    producto.nombre, detalle.cantidad, producto.stock
                )
        self.calcular_total()
        return True

    # ------------------------------------------------------------------
    # Pago
    # ------------------------------------------------------------------
    def registrar_pago(self) -> bool:
        """Confirma el pedido y recien entonces descuenta el stock."""
        self.confirmar_pedido()
        for detalle in self._detalles:
            detalle.producto.descontar_stock(detalle.cantidad)
        self._estado_pago = "PAGADO"
        self._estado_entrega = "EN_PREPARACION"
        return True

    def rechazar_pago(self) -> None:
        self._estado_pago = "RECHAZADO"

    # ------------------------------------------------------------------
    # Regla 2: no despachar sin pago
    # ------------------------------------------------------------------
    def despachar(self, operador: Trabajador) -> bool:
        if not isinstance(operador, Trabajador):
            raise DatoInvalidoError("El despacho debe ser ejecutado por un trabajador.")
        if not operador.puede_despachar():
            raise SinPermisoError("despachar pedidos", operador.rol)
        if self._estado_pago != "PAGADO":
            raise PedidoNoPagadoError(self._id_pedido, self._estado_pago)
        self._estado_entrega = "DESPACHADO"
        return True

    # ------------------------------------------------------------------
    # Polimorfismo de entrega
    # ------------------------------------------------------------------
    def procesar_despacho_entregas(self) -> list[dict]:
        """Ejecuta ``procesar_entrega()`` segun el subtipo de cada producto."""
        resultados = []
        for detalle in self._detalles:
            resultados.append(detalle.producto.procesar_entrega(detalle))
        self._estado_entrega = "ENTREGADO"
        return resultados

    # ------------------------------------------------------------------
    # Totales
    # ------------------------------------------------------------------
    def calcular_total(self) -> float:
        subtotal = sum(detalle.calcular_subtotal() for detalle in self._detalles)
        fletes = 0.0
        for detalle in self._detalles:
            if isinstance(detalle.producto, ProductoFisico):
                fletes += detalle.producto.calcular_flete()
        self._total_flete_clp = round(fletes, 2)
        self._total_final_clp = round(subtotal + fletes, 2)
        return self._total_final_clp

    def to_dict(self) -> dict:
        return {
            "id_pedido": self._id_pedido,
            "id_cliente": self._cliente.id_cliente,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "estado_pago": self._estado_pago,
            "estado_entrega": self._estado_entrega,
            "total_flete_clp": self._total_flete_clp,
            "total_final_clp": self._total_final_clp,
        }

    def __str__(self) -> str:
        return (
            f"Pedido {self._id_pedido} | {self._cliente.nombre} | "
            f"pago {self._estado_pago} | entrega {self._estado_entrega} | "
            f"total ${self._total_final_clp:,.0f} CLP"
        )
