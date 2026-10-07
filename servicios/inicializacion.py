"""Arranque del sistema: crea tablas y carga los datos iniciales."""

from __future__ import annotations

from datetime import datetime, timedelta

from dao.cliente_dao import ClienteDAO
from dao.conexion import ConexionBD
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from model.administrador import Administrador
from model.cliente import Cliente
from model.encargado_bodega import EncargadoBodega
from model.producto_digital import ProductoDigital
from model.producto_electronica import ProductoElectronica
from model.producto_fisico import ProductoFisico
from model.producto_servicio import ProductoServicio

USUARIOS_DEMO = (
    # (nombre de usuario, password, rol)
    ("Maria Gonzalez", "admin1234", "ADMINISTRADOR"),
    ("Juan Perez", "bodega1234", "ENCARGADO_BODEGA"),
)


def preparar_base(conexion: ConexionBD) -> None:
    """Crea el esquema si no existe (requisito de persistencia)."""
    conexion.crear_tablas()


def cargar_datos_iniciales(conexion: ConexionBD, incluir_demo: bool = True) -> None:
    """Siembra usuarios, clientes y catalogo de ejemplo la primera vez."""
    _sembrar_trabajadores(conexion)
    if incluir_demo:
        _sembrar_demo(conexion)


def _sembrar_trabajadores(conexion: ConexionBD) -> None:
    dao = TrabajadorDAO(conexion)
    if dao.contar() > 0:
        return
    admin = Administrador("TRAB-01", "Maria Gonzalez", "maria.gonzalez@clickandgo.cl", 1)
    admin.definir_password("admin1234")
    bodega = EncargadoBodega("TRAB-02", "Juan Perez", "juan.perez@clickandgo.cl", "Bodega Central")
    bodega.definir_password("bodega1234")
    dao.crear(admin)
    dao.crear(bodega)


def _sembrar_demo(conexion: ConexionBD) -> None:
    clientes = ClienteDAO(conexion)
    productos = ProductoDAO(conexion)

    if clientes.contar() == 0:
        clientes.crear(Cliente("CLI-01", "Miguel Troncoso", "19.876.543-0", "RUT"))
        clientes.crear(Cliente("CLI-02", "Alexandy Remicinthe", "alexandy@clickandgo.cl", "EMAIL"))

    if productos.contar() > 0:
        return

    productos.crear(
        ProductoFisico(
            "PROD-F01", "Silla Ergonómica Gamer", 85000.0, 10, peso_kg=14.0, volumen_m3=0.15
        )
    )
    productos.crear(
        ProductoDigital(
            "PROD-D01",
            "Licencia Antivirus Pro",
            24990.0,
            100,
            "https://cdn.clickandgo.cl/downloads/antivirus.iso",
            "CKG-2026-X94B",
            450.0,
        )
    )
    productos.crear(
        ProductoServicio(
            "PROD-S01",
            "Instalación Red Domiciliaria",
            40000.0,
            15,
            datetime.now() + timedelta(days=7),
            "Av. Apoquindo 4500, Las Condes",
            2,
        )
    )
    productos.crear(
        ProductoElectronica(
            "PROD-E01", "Monitor 4K Importado", 250.0, 5, peso_kg=4.5, volumen_m3=0.03
        )
    )


def datos_demo_json(conexion: ConexionBD) -> dict:
    """Resumen serializable usado por la capa web."""
    return {
        "trabajadores": [t.to_dict() for t in TrabajadorDAO(conexion).listar()],
        "clientes": [c.to_dict() for c in ClienteDAO(conexion).listar()],
        "productos": [p.to_dict() for p in ProductoDAO(conexion).listar()],
    }
