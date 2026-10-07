#!/usr/bin/env python3
"""Demostracion automatica de ClickAndGo (sin interaccion).

Recorre, en el mismo orden que la rubrica de la Evaluacion Sumativa N2:

1. Un dato invalido rechazado por la validacion.
2. El CRUD de una entidad principal.
3. Una transaccion con sus lineas de detalle guardada en la base de datos.
4. Las dos reglas del negocio impidiendo una operacion.
5. El precio calculado con el indicador obtenido desde la API.
6. Que hace el programa cuando la API no responde.

Ejecutar:  python demo.py
"""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from dao.cliente_dao import ClienteDAO
from dao.conexion import ConexionBD
from dao.pedido_dao import PedidoDAO
from dao.producto_dao import ProductoDAO
from model.cliente import Cliente
from model.encargado_bodega import EncargadoBodega
from model.excepciones import (
    DatoInvalidoError,
    PedidoNoPagadoError,
    StockInsuficienteError,
)
from model.pedido import Pedido
from model.producto_digital import ProductoDigital
from model.producto_electronica import ProductoElectronica
from model.producto_fisico import ProductoFisico
from model.producto_servicio import ProductoServicio
from servicios.indicador_dolar import ServicioIndicadorDolar
from servicios.inicializacion import cargar_datos_iniciales, preparar_base

LINEA = "=" * 78


def titulo(texto: str) -> None:
    print("\n" + LINEA)
    print(f"  {texto}")
    print(LINEA)


def main() -> None:
    carpeta = tempfile.TemporaryDirectory()
    conexion = ConexionBD(Path(carpeta.name) / "demo.db")
    preparar_base(conexion)
    cargar_datos_iniciales(conexion)
    clientes, productos, pedidos = ClienteDAO(conexion), ProductoDAO(conexion), PedidoDAO(conexion)

    print(LINEA)
    print("  ClickAndGo - DEMOSTRACION AUTOMATICA DE LA EVALUACION SUMATIVA N2")
    print("  INACAP TI3V21 - Programacion Orientada a Objeto Seguro")
    print(LINEA)

    # 1. Validacion obligatoria ----------------------------------------
    titulo("1. DATO INVALIDO RECHAZADO POR LA VALIDACION")
    try:
        Cliente("CLI-X", "Cliente Invalido", "cliente@", "EMAIL")
    except DatoInvalidoError as error:
        print(f"  [X] Rechazado sin detener el programa: {error}")
    valido = Cliente("CLI-100", "Cliente Demo", "cliente@correo.cl", "EMAIL")
    clientes.crear(valido)
    print(f"  [OK] Cliente valido aceptado: {valido}")

    # 2. CRUD de una entidad principal ---------------------------------
    titulo("2. CRUD DE UNA ENTIDAD PRINCIPAL (productos)")
    silla = ProductoFisico("DEMO-F01", "Silla Ergonómica", 85000.0, 4, 14.0, 0.15)
    productos.crear(silla)
    print(f"  [C] Creado  : {silla}")
    silla.stock = 5
    productos.actualizar(silla)
    print(f"  [U] Modificado: stock = {silla.stock}")
    print("  [R] Listado:")
    for producto in productos.listar():
        print(f"        - {producto}")
    productos.crear(ProductoFisico("DEMO-BORRAR", "Producto Temporal", 1000.0, 1, 1.0, 0.01))
    productos.eliminar("DEMO-BORRAR")
    print("  [D] Eliminado: 'Producto Temporal' ya no esta en el catalogo")

    # 3. Transaccion con lineas de detalle -----------------------------
    titulo("3. TRANSACCION CON LINEAS DE DETALLE")
    indicador = ServicioIndicadorDolar()
    valor_dolar, advertencia = indicador.valor_para_calculo()
    if advertencia:
        print(f"  [!] {advertencia}")
    valor_dolar = valor_dolar.valor if valor_dolar else 950.0
    digital = ProductoDigital(
        "DEMO-D01", "Licencia Antivirus", 24990.0, 100,
        "https://cdn.clickandgo.cl/antivirus.iso", "CKG-2026-X94B", 450.0,
    )
    servicio = ProductoServicio(
        "DEMO-S01", "Instalación Red", 40000.0, 15,
        datetime.now() + timedelta(days=7), "Av. Apoquindo 4500", 2,
    )
    electronica = ProductoElectronica("DEMO-E01", "Monitor 4K Importado", 250.0, 5, 4.5, 0.03)
    for producto in (digital, servicio, electronica):
        productos.crear(producto)

    pedido = Pedido("DEMO-1001", valido)
    pedido.agregar_linea(silla, 2)
    pedido.agregar_linea(digital, 1)
    pedido.agregar_linea(electronica, 1, valor_dolar)
    pedidos.crear(pedido)
    recuperado = pedidos.obtener("DEMO-1001")
    print(f"  Pedido {recuperado.id_pedido} guardado con {len(recuperado.detalles)} lineas:")
    for detalle in recuperado.detalles:
        print(f"    - {detalle}")
    print(f"  Total con flete: ${recuperado.total_final_clp:,.0f} CLP")

    # 4. Las dos reglas del negocio ------------------------------------
    titulo("4. LAS DOS REGLAS QUE IMPIDEN UNA OPERACION")
    escaso = ProductoFisico("DEMO-STK", "Producto Escaso", 10000.0, 3, 1.0, 0.01)
    productos.crear(escaso)
    pedido_sin_stock = Pedido("DEMO-1002", valido)
    pedido_sin_stock.agregar_linea(escaso, 5)
    pedidos.crear(pedido_sin_stock)
    try:
        pedido_sin_stock.confirmar_pedido()
    except StockInsuficienteError as error:
        print(f"  [X] Regla 1 (stock): {error}")
        print(f"      El stock no cambio: {escaso.stock} unidades.")

    despachador = EncargadoBodega("DEMO-T02", "Juan Pérez", "juan.perez@clickandgo.cl")
    try:
        recuperado.despachar(despachador)
    except PedidoNoPagadoError as error:
        print(f"  [X] Regla 2 (pago): {error}")

    # Pago y despacho exitoso ------------------------------------------
    recuperado.registrar_pago()
    pedidos.actualizar_estado(
        recuperado.id_pedido, recuperado.estado_pago,
        recuperado.estado_entrega, recuperado.total_final_clp,
    )
    print(f"  [OK] Tras registrar el pago, el pedido quedo {recuperado.estado_pago}")
    recuperado.despachar(despachador)
    print(f"  [OK] Despacho autorizado por {despachador.nombre} ({despachador.rol})")
    print("  [OK] Entregas polimorficas:")
    for resultado in recuperado.procesar_despacho_entregas():
        print(f"       [{resultado['tipo']}] {resultado['producto']}: {resultado['mensaje']}")

    # 5. Precio con indicador externo ----------------------------------
    titulo("5. PRECIO CALCULADO CON EL DOLAR DEL DIA (mindicador.cl)")
    print(f"  Dolar usado: ${valor_dolar:,.2f} CLP/USD")
    print(f"  {electronica.nombre}: USD {electronica.precio_usd:,.2f} x "
          f"${valor_dolar:,.2f} = ${electronica.calcular_precio_final(valor_dolar):,.0f} CLP")

    # 6. Continuidad si la API no responde -----------------------------
    titulo("6. QUE HACE EL PROGRAMA CUANDO LA API NO RESPONDE")
    sin_conexion = ServicioIndicadorDolar(
        url="https://host-invalido.invalid/api/dolar",
        timeout=3.0,
        ruta_respaldo=Path(carpeta.name) / "respaldo.json",
    )
    indicador2, aviso = sin_conexion.valor_para_calculo()
    print(f"  [!] {aviso}")
    print("  [OK] El programa informa el problema y continua funcionando.")

    print("\n" + LINEA)
    print("  DEMOSTRACION COMPLETA: el sistema no se detuvo en ningun caso.")
    print(LINEA + "\n")
    carpeta.cleanup()


if __name__ == "__main__":
    main()
