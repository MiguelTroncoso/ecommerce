"""Clase base abstracta del catalogo de ClickAndGo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from model.excepciones import DatoInvalidoError

if TYPE_CHECKING:  # pragma: no cover - solo para tipado
    from model.detalle_pedido import DetallePedido


class Producto(ABC):
    """Contrato comun de todo item de inventario.

    Define los atributos privados del catalogo y las dos operaciones
    polimorficas: ``procesar_entrega()`` y ``calcular_precio_final()``.
    """

    TIPO = "GENERICO"

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio_base_clp: float,
        stock: int,
    ) -> None:
        self._id_producto = ""
        self._nombre = ""
        self._precio_base_clp = 0.0
        self._stock = 0
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio_base_clp = precio_base_clp
        self.stock = stock

    # ------------------------------------------------------------------
    # Propiedades con validacion en el setter
    # ------------------------------------------------------------------
    @property
    def id_producto(self) -> str:
        return self._id_producto

    @id_producto.setter
    def id_producto(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise DatoInvalidoError("El identificador interno del producto no puede estar vacio.")
        self._id_producto = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if len(valor) < 3:
            raise DatoInvalidoError("El nombre del producto debe tener al menos 3 caracteres.")
        self._nombre = valor

    @property
    def precio_base_clp(self) -> float:
        return self._precio_base_clp

    @precio_base_clp.setter
    def precio_base_clp(self, valor: float) -> None:
        valor = float(valor)
        if valor < 0:
            raise DatoInvalidoError("El precio base no puede ser negativo.")
        self._precio_base_clp = round(valor, 2)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatoInvalidoError("El stock debe ser un numero entero.")
        if valor < 0:
            raise DatoInvalidoError("El stock no puede ser negativo.")
        self._stock = valor

    # ------------------------------------------------------------------
    # Operaciones polimorficas
    # ------------------------------------------------------------------
    @abstractmethod
    def procesar_entrega(self, detalle: "DetallePedido") -> dict:
        """Resuelve la entrega segun la mecanica del subtipo de producto."""

    @abstractmethod
    def calcular_precio_final(self, valor_dolar: float | None = None) -> float:
        """Calcula el precio de venta, opcionalmente con un indicador externo."""

    # ------------------------------------------------------------------
    # Inventario
    # ------------------------------------------------------------------
    def tiene_stock_suficiente(self, cantidad: int) -> bool:
        return self._stock >= int(cantidad)

    def descontar_stock(self, cantidad: int) -> None:
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad a descontar debe ser mayor que cero.")
        if not self.tiene_stock_suficiente(cantidad):
            from model.excepciones import StockInsuficienteError

            raise StockInsuficienteError(self._nombre, cantidad, self._stock)
        self._stock -= cantidad

    def reponer_stock(self, cantidad: int) -> None:
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad a reponer debe ser mayor que cero.")
        self._stock += cantidad

    @property
    def tipo(self) -> str:
        return self.TIPO

    @property
    def descripcion_corta(self) -> str:
        return f"{self._nombre} [{self.TIPO}]"

    def to_dict(self) -> dict:
        """Representacion plana usada por la capa DAO."""
        return {
            "id_producto": self._id_producto,
            "tipo": self.TIPO,
            "nombre": self._nombre,
            "precio_base_clp": self._precio_base_clp,
            "precio_usd": 0.0,
            "stock": self._stock,
            "peso_kg": 0.0,
            "volumen_m3": 0.0,
            "tarifa_flete_base": 0.0,
            "enlace_descarga": "",
            "licencia_activacion": "",
            "peso_archivo_mb": 0.0,
            "fecha_agendada": "",
            "direccion_visita": "",
            "duracion_estimada_horas": 0,
            "garantia_meses": 0,
        }

    def __str__(self) -> str:
        return f"{self.descripcion_corta} - ${self._precio_base_clp:,.0f} CLP - stock {self._stock}"
