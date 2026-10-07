"""Modelo de dominio ClickAndGo (una clase por archivo).

El paquete expone las entidades del diagrama UML de la Evaluacion Sumativa N1
ya adaptadas a la Evaluacion Sumativa N2 (persistencia, validacion, API y
excepciones propias de negocio).
"""

from model.administrador import Administrador
from model.cliente import Cliente
from model.detalle_pedido import DetallePedido
from model.encargado_bodega import EncargadoBodega
from model.excepciones import (
    AutenticacionError,
    ClickAndGoError,
    DatoInvalidoError,
    IdentificadorInvalidoError,
    IndicadorNoDisponibleError,
    PedidoNoPagadoError,
    PedidoVacioError,
    RegistroNoEncontradoError,
    SinPermisoError,
    StockInsuficienteError,
)
from model.pedido import Pedido
from model.producto import Producto
from model.producto_digital import ProductoDigital
from model.producto_electronica import ProductoElectronica
from model.producto_fisico import ProductoFisico
from model.producto_servicio import ProductoServicio
from model.trabajador import Trabajador

__all__ = [
    "Administrador",
    "Cliente",
    "DetallePedido",
    "EncargadoBodega",
    "Pedido",
    "Producto",
    "ProductoDigital",
    "ProductoElectronica",
    "ProductoFisico",
    "ProductoServicio",
    "Trabajador",
    "AutenticacionError",
    "ClickAndGoError",
    "DatoInvalidoError",
    "IdentificadorInvalidoError",
    "IndicadorNoDisponibleError",
    "PedidoNoPagadoError",
    "PedidoVacioError",
    "RegistroNoEncontradoError",
    "SinPermisoError",
    "StockInsuficienteError",
]
