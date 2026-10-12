#!/usr/bin/env python3
"""ClickAndGo 2.0 - Sistema de gestion e-commerce por consola.

Evaluacion Sumativa N2 y N3 - Programacion Orientada a Objeto Seguro (TI3V21)

Arquitectura:

    model/      clases del diagrama UML (una por archivo, con herencia,
                encapsulamiento y excepciones propias de negocio)
    dao/        persistencia SQLite con consultas parametrizadas
    servicios/  validacion de entradas, codigos automaticos y API del dolar
                (mindicador.cl con respaldo en findic.cl)
    main.py     menu de consola que orquesta todo

Ejecucion:

    python main.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parent
if str(RUTA_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RUTA_PROYECTO))

from dao.cliente_dao import ClienteDAO  # noqa: E402
from dao.conexion import ConexionBD  # noqa: E402
from dao.pedido_dao import PedidoDAO  # noqa: E402
from dao.producto_dao import ProductoDAO  # noqa: E402
from dao.trabajador_dao import TrabajadorDAO  # noqa: E402
from model.cliente import Cliente  # noqa: E402
from model.excepciones import (  # noqa: E402
    ClickAndGoError,
    RegistroNoEncontradoError,
    SinPermisoError,
)
from model.pedido import Pedido  # noqa: E402
from model.producto_digital import ProductoDigital  # noqa: E402
from model.producto_electronica import ProductoElectronica  # noqa: E402
from model.producto_fisico import ProductoFisico  # noqa: E402
from model.producto_servicio import ProductoServicio  # noqa: E402
from servicios.codigos import GeneradorCodigos  # noqa: E402
from servicios.consola import (  # noqa: E402
    aviso,
    azul,
    gris,
    habilitar_color,
    info,
    negrita,
    ok,
    panel,
    paso,
    subtitulo,
    tabla,
    titulo,
)
from servicios.indicador_dolar import ServicioIndicadorDolar  # noqa: E402
from servicios.inicializacion import cargar_datos_iniciales, preparar_base  # noqa: E402
from servicios.validador import (  # noqa: E402
    pedir_decimal,
    pedir_entero,
    pedir_fecha_futura,
    pedir_identificador,
    pedir_opcion,
    pedir_seleccion,
    pedir_texto,
    pedir_url,
)

CLP = "${:,.0f}"


class AplicacionClickAndGo:
    """Menu principal del sistema. ``entrada`` permite inyectar otro origen."""

    def __init__(self, conexion: ConexionBD | None = None, entrada=input,
                 color: bool | None = None) -> None:
        habilitar_color(color)
        self._entrada = entrada
        self._bd = conexion or ConexionBD()
        self._clientes = ClienteDAO(self._bd)
        self._productos = ProductoDAO(self._bd)
        self._pedidos = PedidoDAO(self._bd)
        self._trabajadores = TrabajadorDAO(self._bd)
        self._codigos = GeneradorCodigos(self._bd)
        self._dolar = ServicioIndicadorDolar()
        # El esquema se crea al construir la aplicacion: asi el programa
        # siempre parte desde una base de datos consistente.
        preparar_base(self._bd)
        cargar_datos_iniciales(self._bd, incluir_demo=False)
        self._sesion = self._trabajador_por_defecto()
        self._valor_dolar_ultimo: float | None = None
        self._dolar_consultado = False
        self._activo = True

    def _trabajador_por_defecto(self):
        trabajadores = self._trabajadores.listar()
        if trabajadores:
            return trabajadores[0]
        raise RegistroNoEncontradoError(
            "No hay trabajadores registrados: la base de datos no se inicializo."
        )

    # ==================================================================
    # Ciclo principal
    # ==================================================================
    def ejecutar(self) -> None:
        cargar_datos_iniciales(self._bd)
        self._bienvenida()
        while self._activo:
            self._mostrar_menu()
            opcion = pedir_opcion("  Opcion", self._opciones_menu(), self._entrada)
            if opcion is None:
                continue
            try:
                self._despachar_menu(opcion)
            except ClickAndGoError as error:
                aviso(f"Operacion no realizada: {error}")
            except sqlite3.IntegrityError as error:
                aviso(f"El registro no se pudo guardar: {error}")
            except (ValueError, TypeError) as error:
                aviso(f"Dato invalido: {error}")
            except KeyboardInterrupt:
                print("\n\n  Sesion finalizada por el usuario (Ctrl+C).")
                self._activo = False
            except Exception as error:  # red de seguridad: informa y continua
                aviso(f"Error inesperado controlado: {type(error).__name__}: {error}")

    @staticmethod
    def _opciones_menu() -> list[str]:
        return ["1", "2", "3", "4", "5", "6", "7", "0"]

    def _bienvenida(self) -> None:
        barra = "=" * 78
        print(barra)
        print("   " + negrita("ClickAndGo") + "  |  Sistema de gestion e-commerce")
        print("   INACAP TI3V21 - Evaluacion Sumativa N2 y N3 (POO Seguro)")
        print(barra)
        print(f"   Base de datos : {self._bd.ruta}")
        print(f"   Operador      : {self._sesion.nombre} ({self._sesion.rol})")
        print(barra)
        print(gris("   Los codigos de clientes y productos se generan automaticamente:"))
        print(gris("   C01 cliente | F01 fisico | D01 digital | S01 servicio | E01 electronica"))

    def _mostrar_menu(self) -> None:
        titulo("MENU PRINCIPAL")
        opciones = [
            ("1", "Clientes", "registrar, listar, modificar y eliminar"),
            ("2", "Productos", "catalogo con los cuatro tipos"),
            ("3", "Pedidos", "venta, pago, despacho y entrega"),
            ("4", "Dolar del dia", "precio de la electronica importada"),
            ("5", "Trabajadores", "roles y permisos (RBAC)"),
            ("6", "Iniciar sesion", "cambiar de operador"),
            ("7", "Datos de ejemplo", "cargar catalogo de demostracion"),
            ("0", "Salir", ""),
        ]
        for numero, nombre, detalle in opciones:
            etiqueta = f"  {numero}. {nombre}"
            if detalle:
                print(f"{etiqueta:<24}{gris(detalle)}")
            else:
                print(etiqueta)
        print(f"\n  Sesion activa: {negrita(self._sesion.nombre)} ({self._sesion.rol})")

    def _despachar_menu(self, opcion: str) -> None:
        acciones = {
            "1": self._menu_clientes,
            "2": self._menu_productos,
            "3": self._menu_pedidos,
            "4": self._calcular_precio_dolar,
            "5": self._listar_trabajadores,
            "6": self._iniciar_sesion,
            "7": self._cargar_demo,
            "0": self._salir,
        }
        acciones[opcion]()

    def _salir(self) -> None:
        self._activo = False
        print("\n  Gracias por usar ClickAndGo. Hasta pronto.\n")

    # ==================================================================
    # Utilidades de seleccion
    # ==================================================================
    def _elegir_cliente(self, mensaje: str = "  Numero o codigo del cliente"):
        clientes = self._clientes.listar()
        if not clientes:
            aviso("No hay clientes registrados. Cree uno primero (opcion 1).")
            return None
        return pedir_seleccion(
            clientes,
            mensaje,
            lambda cliente: f"{cliente.id_cliente}  {cliente.nombre}  "
                            f"({cliente.tipo_identificador}: {cliente.identificador})",
            lambda cliente: cliente.id_cliente,
            self._entrada,
        )

    def _elegir_producto(self, mensaje: str = "  Numero o codigo del producto"):
        productos = self._productos.listar()
        if not productos:
            aviso("No hay productos en el catalogo. Cree uno primero (opcion 2).")
            return None
        return pedir_seleccion(
            productos,
            mensaje,
            lambda producto: f"{producto.id_producto}  {producto.nombre}  "
                             f"({producto.tipo}, {self._precio_texto(producto)}, "
                             f"stock {producto.stock})",
            lambda producto: producto.id_producto,
            self._entrada,
        )

    def _elegir_pedido(self, mensaje: str = "  Numero o codigo del pedido"):
        pedidos = self._pedidos.listar()
        if not pedidos:
            aviso("No hay pedidos registrados. Cree uno primero (opcion 3).")
            return None
        return pedir_seleccion(
            pedidos,
            mensaje,
            lambda pedido: f"{pedido.id_pedido}  {pedido.cliente.nombre}  "
                           f"{pedido.estado_pago}/{pedido.estado_entrega}  "
                           f"{CLP.format(pedido.total_final_clp)}",
            lambda pedido: pedido.id_pedido,
            self._entrada,
        )

    @staticmethod
    def _precio_texto(producto) -> str:
        if isinstance(producto, ProductoElectronica):
            return f"USD {producto.precio_usd:,.2f}"
        return CLP.format(producto.precio_base_clp)

    # ==================================================================
    # Clientes
    # ==================================================================
    def _menu_clientes(self) -> None:
        while True:
            subtitulo("CLIENTES")
            print("  1. Registrar cliente      (el codigo se asigna automaticamente)")
            print("  2. Listar clientes")
            print("  3. Modificar cliente")
            print("  4. Eliminar cliente")
            print("  0. Volver")
            opcion = pedir_opcion("  Opcion", ["1", "2", "3", "4", "0"], self._entrada)
            if opcion in (None, "0"):
                return
            if opcion == "1":
                self._crear_cliente()
            elif opcion == "2":
                self._listar_clientes()
            elif opcion == "3":
                self._modificar_cliente()
            elif opcion == "4":
                self._eliminar_cliente()

    def _crear_cliente(self) -> None:
        subtitulo("REGISTRAR CLIENTE")
        print(gris("  El sistema asignara el codigo automaticamente (C01, C02, ...)."))
        nombre = pedir_texto(paso(1, 3, "Nombre completo"), self._entrada, 3, 80)
        tipo = pedir_opcion(
            paso(2, 3, "Tipo de identificador (1=RUT, 2=EMAIL)"), ["1", "2"], self._entrada
        )
        if tipo is None:
            return
        tipo = "RUT" if tipo == "1" else "EMAIL"
        identificador = pedir_identificador(
            paso(3, 3, "RUT (ej: 19.876.543-0)" if tipo == "RUT"
                 else "Correo (ej: cliente@correo.cl)"),
            tipo,
            self._entrada,
        )
        codigo = self._codigos.siguiente_cliente()
        cliente = Cliente(codigo, nombre, identificador, tipo)
        self._clientes.crear(cliente)
        panel("CLIENTE REGISTRADO", [
            ("Codigo asignado", cliente.id_cliente),
            ("Nombre", cliente.nombre),
            ("Identificador", f"{cliente.tipo_identificador}: {cliente.identificador}"),
        ])

    def _listar_clientes(self) -> list:
        subtitulo("LISTADO DE CLIENTES")
        clientes = self._clientes.listar()
        if not clientes:
            aviso("No hay clientes registrados todavia.")
            return []
        tabla(
            ["CODIGO", "NOMBRE", "TIPO", "IDENTIFICADOR"],
            [[c.id_cliente, c.nombre, c.tipo_identificador, c.identificador] for c in clientes],
        )
        return clientes

    def _modificar_cliente(self) -> None:
        cliente = self._elegir_cliente()
        if cliente is None:
            return
        subtitulo(f"MODIFICAR CLIENTE {cliente.id_cliente}")
        nombre = pedir_texto(
            paso(1, 2, f"Nuevo nombre (Enter para mantener '{cliente.nombre}')"),
            self._entrada, 3, 80, permitir_vacio=True,
        )
        if nombre:
            cliente.nombre = nombre
        tipo = pedir_opcion(
            paso(2, 2, "Tipo de identificador (1=RUT, 2=EMAIL)"), ["1", "2"], self._entrada
        )
        if tipo is None:
            return
        tipo = "RUT" if tipo == "1" else "EMAIL"
        cliente.tipo_identificador = tipo
        cliente.identificador = pedir_identificador("  Nuevo identificador", tipo, self._entrada)
        self._clientes.actualizar(cliente)
        panel("CLIENTE ACTUALIZADO", [
            ("Codigo", cliente.id_cliente),
            ("Nombre", cliente.nombre),
            ("Identificador", f"{cliente.tipo_identificador}: {cliente.identificador}"),
        ])

    def _eliminar_cliente(self) -> None:
        cliente = self._elegir_cliente()
        if cliente is None:
            return
        confirmar = pedir_opcion(
            f"  Confirma eliminar a {cliente.nombre} ({cliente.id_cliente})? (1=Si, 0=No)",
            ["1", "0"], self._entrada,
        )
        if confirmar != "1":
            info("Operacion cancelada.")
            return
        if self._clientes.eliminar(cliente.id_cliente):
            ok(f"Cliente {cliente.id_cliente} eliminado.")

    # ==================================================================
    # Productos
    # ==================================================================
    def _menu_productos(self) -> None:
        while True:
            subtitulo("CATALOGO DE PRODUCTOS")
            print("  1. Registrar producto    (el codigo se asigna automaticamente)")
            print("  2. Listar catalogo")
            print("  3. Modificar producto    (nombre, precio y stock)")
            print("  4. Eliminar producto")
            print("  0. Volver")
            opcion = pedir_opcion("  Opcion", ["1", "2", "3", "4", "0"], self._entrada)
            if opcion in (None, "0"):
                return
            if opcion == "1":
                self._crear_producto()
            elif opcion == "2":
                self._listar_productos()
            elif opcion == "3":
                self._modificar_producto()
            elif opcion == "4":
                self._eliminar_producto()

    def _validar_permiso_catalogo(self) -> None:
        if not self._sesion.puede_modificar_catalogo():
            raise SinPermisoError("modificar el catalogo", self._sesion.rol)

    def _crear_producto(self) -> None:
        self._validar_permiso_catalogo()
        subtitulo("REGISTRAR PRODUCTO")
        print("  Tipos disponibles:")
        print("   1 = Producto fisico        (codigo F01, F02, ...)")
        print("   2 = Producto digital       (codigo D01, D02, ...)")
        print("   3 = Servicio tecnico       (codigo S01, S02, ...)")
        print("   4 = Electronica importada  (codigo E01, E02, ... USD)")
        print(gris("  El codigo se asigna automaticamente segun el tipo."))

        tipo = pedir_opcion(paso(1, 3, "Tipo de producto"), ["1", "2", "3", "4"], self._entrada)
        if tipo is None:
            return
        extras = {"1": 3, "2": 4, "3": 4, "4": 4}[tipo]
        total = 3 + extras
        nombre = pedir_texto(paso(2, total, "Nombre del producto"), self._entrada, 3, 60)
        stock = pedir_entero(paso(3, total, "Stock inicial"), self._entrada, 0, 1_000_000)

        producto = None
        if tipo == "1":
            precio = pedir_decimal(paso(4, total, "Precio base en CLP"), self._entrada, 0)
            peso = pedir_decimal(paso(5, total, "Peso en kg"), self._entrada, 0.001)
            volumen = pedir_decimal(paso(6, total, "Volumen en m3"), self._entrada, 0.0001)
            codigo = self._codigos.siguiente_producto("FISICO")
            producto = ProductoFisico(codigo, nombre, precio, stock, peso, volumen)
        elif tipo == "2":
            precio = pedir_decimal(paso(4, total, "Precio base en CLP"), self._entrada, 0)
            enlace = pedir_url(paso(5, total, "Enlace de descarga"), self._entrada)
            licencia = pedir_texto(paso(6, total, "Licencia de activacion"), self._entrada, 4, 40)
            peso_mb = pedir_decimal(paso(7, total, "Peso del archivo en MB"), self._entrada, 0)
            codigo = self._codigos.siguiente_producto("DIGITAL")
            producto = ProductoDigital(codigo, nombre, precio, stock, enlace, licencia, peso_mb)
        elif tipo == "3":
            precio = pedir_decimal(paso(4, total, "Precio base en CLP"), self._entrada, 0)
            fecha = pedir_fecha_futura(
                paso(5, total, "Fecha y hora (AAAA-MM-DD HH:MM)"), self._entrada
            )
            direccion = pedir_texto(paso(6, total, "Direccion de la visita"), self._entrada, 5, 80)
            duracion = pedir_entero(paso(7, total, "Duracion estimada en horas"), self._entrada, 1, 24)
            codigo = self._codigos.siguiente_producto("SERVICIO")
            producto = ProductoServicio(
                codigo, nombre, precio, stock, fecha, direccion, duracion
            )
        else:
            precio_usd = pedir_decimal(paso(4, total, "Precio en USD"), self._entrada, 0.01)
            peso = pedir_decimal(paso(5, total, "Peso en kg"), self._entrada, 0.001)
            volumen = pedir_decimal(paso(6, total, "Volumen en m3"), self._entrada, 0.0001)
            garantia = pedir_entero(paso(7, total, "Garantia en meses"), self._entrada, 0, 120)
            codigo = self._codigos.siguiente_producto("ELECTRONICA")
            producto = ProductoElectronica(
                codigo, nombre, precio_usd, stock, peso, volumen, garantia
            )

        self._productos.crear(producto)
        panel("PRODUCTO REGISTRADO", [
            ("Codigo asignado", producto.id_producto),
            ("Nombre", producto.nombre),
            ("Tipo", producto.tipo),
            ("Precio", self._precio_texto(producto)),
            ("Stock", str(producto.stock)),
        ])

    def _listar_productos(self, tipo: str | None = None) -> list:
        subtitulo("CATALOGO" + (f" - {tipo}" if tipo else ""))
        productos = self._productos.listar(tipo)
        if not productos:
            aviso("No hay productos registrados todavia.")
            return []
        tabla(
            ["CODIGO", "TIPO", "NOMBRE", "PRECIO", "STOCK"],
            [[p.id_producto, p.tipo, p.nombre, self._precio_texto(p), str(p.stock)]
             for p in productos],
            ["<", "<", "<", ">", ">"],
        )
        return productos

    def _modificar_producto(self) -> None:
        self._validar_permiso_catalogo()
        producto = self._elegir_producto()
        if producto is None:
            return
        subtitulo(f"MODIFICAR PRODUCTO {producto.id_producto}")
        nuevo_nombre = pedir_texto(
            paso(1, 3, f"Nuevo nombre (Enter para mantener '{producto.nombre}')"),
            self._entrada, 3, 60, permitir_vacio=True,
        )
        if nuevo_nombre:
            producto.nombre = nuevo_nombre
        producto.stock = pedir_entero(
            paso(2, 3, f"Nuevo stock (actual {producto.stock})"),
            self._entrada, 0, 1_000_000,
        )
        if isinstance(producto, ProductoElectronica):
            producto.precio_usd = pedir_decimal(
                paso(3, 3, f"Nuevo precio USD (actual {producto.precio_usd:,.2f})"),
                self._entrada, 0.01,
            )
        else:
            producto.precio_base_clp = pedir_decimal(
                paso(3, 3, f"Nuevo precio CLP (actual {CLP.format(producto.precio_base_clp)})"),
                self._entrada, 0,
            )
        self._productos.actualizar(producto)
        panel("PRODUCTO ACTUALIZADO", [
            ("Codigo", producto.id_producto),
            ("Nombre", producto.nombre),
            ("Precio", self._precio_texto(producto)),
            ("Stock", str(producto.stock)),
        ])

    def _eliminar_producto(self) -> None:
        self._validar_permiso_catalogo()
        producto = self._elegir_producto()
        if producto is None:
            return
        confirmar = pedir_opcion(
            f"  Confirma eliminar '{producto.nombre}' ({producto.id_producto})? (1=Si, 0=No)",
            ["1", "0"], self._entrada,
        )
        if confirmar != "1":
            info("Operacion cancelada.")
            return
        if self._productos.eliminar(producto.id_producto):
            ok(f"Producto {producto.id_producto} eliminado del catalogo.")

    # ==================================================================
    # Pedidos
    # ==================================================================
    def _menu_pedidos(self) -> None:
        while True:
            subtitulo("PEDIDOS")
            print("  1. Crear pedido            (multi-linea)")
            print("  2. Listar pedidos")
            print("  3. Ver detalle de un pedido")
            print("  4. Confirmar pedido        (Regla 1: stock suficiente)")
            print("  5. Registrar pago")
            print("  6. Despachar pedido        (Regla 2: pedido pagado)")
            print("  7. Procesar entrega        (comportamiento polimorfico)")
            print("  8. Eliminar pedido")
            print("  0. Volver")
            opcion = pedir_opcion(
                "  Opcion", ["1", "2", "3", "4", "5", "6", "7", "8", "0"], self._entrada
            )
            if opcion in (None, "0"):
                return
            if opcion == "1":
                self._crear_pedido()
            elif opcion == "2":
                self._listar_pedidos()
            elif opcion == "3":
                self._ver_detalle_pedido()
            elif opcion == "4":
                self._confirmar_pedido()
            elif opcion == "5":
                self._registrar_pago()
            elif opcion == "6":
                self._despachar_pedido()
            elif opcion == "7":
                self._procesar_entrega()
            elif opcion == "8":
                self._eliminar_pedido()

    def _valor_dolar(self) -> float | None:
        """Obtiene el dolar del dia informando cualquier falla."""
        self._dolar_consultado = True
        indicador, advertencia = self._dolar.valor_para_calculo()
        if advertencia:
            aviso(advertencia)
        if indicador is None:
            aviso("Sin valor de dolar disponible: no es posible cotizar importados.")
            return None
        self._valor_dolar_ultimo = indicador.valor
        info(f"Dolar utilizado: {indicador}")
        return indicador.valor

    def _valor_dolar_si_falta(self) -> float | None:
        """Consulta la API una sola vez, y solo si un importado lo requiere."""
        if self._valor_dolar_ultimo is not None:
            return self._valor_dolar_ultimo
        if self._dolar_consultado:
            return None
        return self._valor_dolar()

    def _crear_pedido(self) -> None:
        subtitulo("NUEVO PEDIDO")
        cliente = self._elegir_cliente("  Numero o codigo del cliente")
        if cliente is None:
            return
        pedido = Pedido(self._codigos.siguiente_pedido(), cliente)
        info(f"Numero de pedido asignado automaticamente: {pedido.id_pedido}")

        while True:
            productos = self._listar_productos()
            if not productos:
                return
            producto = pedir_seleccion(
                productos,
                "  Producto a agregar (0 para terminar)",
                lambda p: f"{p.id_producto}  {p.nombre}  "
                          f"({p.tipo}, {self._precio_texto(p)}, stock {p.stock})",
                lambda p: p.id_producto,
                self._entrada,
                descripcion_cancelar="terminar el pedido",
            )
            if producto is None:
                break
            cantidad = pedir_entero("  Cantidad", self._entrada, 1, 100000)
            valor_dolar = None
            if isinstance(producto, ProductoElectronica):
                valor_dolar = self._valor_dolar_si_falta()
                if valor_dolar is None:
                    aviso("Sin valor del dolar no se puede cotizar este producto importado.")
                    continue
            detalle = pedido.agregar_linea(producto, cantidad, valor_dolar)
            ok(f"Linea agregada: {detalle}")

        if not pedido.detalles:
            aviso("El pedido quedo sin lineas: no se guarda.")
            return
        self._pedidos.crear(pedido)
        panel("PEDIDO GUARDADO", [
            ("Numero", pedido.id_pedido),
            ("Cliente", f"{pedido.cliente.id_cliente} - {pedido.cliente.nombre}"),
            ("Lineas de detalle", str(len(pedido.detalles))),
            ("Flete", f"{CLP.format(pedido.total_flete_clp)} CLP"),
            ("TOTAL", f"{CLP.format(pedido.total_final_clp)} CLP"),
        ])

    def _listar_pedidos(self) -> list:
        subtitulo("PEDIDOS REGISTRADOS")
        pedidos = self._pedidos.listar()
        if not pedidos:
            aviso("No hay pedidos registrados todavia.")
            return []
        tabla(
            ["NUMERO", "CLIENTE", "FECHA", "PAGO", "ENTREGA", "TOTAL"],
            [[p.id_pedido, p.cliente.nombre, f"{p.fecha_creacion:%d/%m/%Y}",
              p.estado_pago, p.estado_entrega, CLP.format(p.total_final_clp)] for p in pedidos],
            ["<", "<", "<", "<", "<", ">"],
        )
        return pedidos

    def _ver_detalle_pedido(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        subtitulo(f"DETALLE DEL PEDIDO {pedido.id_pedido}")
        print(f"  Cliente        : {pedido.cliente.nombre} "
              f"({pedido.cliente.tipo_identificador}: {pedido.cliente.identificador})")
        print(f"  Fecha          : {pedido.fecha_creacion:%Y-%m-%d %H:%M}")
        print(f"  Estado de pago : {pedido.estado_pago}")
        print(f"  Estado entrega : {pedido.estado_entrega}")
        print("\n  Lineas de detalle:")
        tabla(
            ["#", "PRODUCTO", "CANT", "PRECIO UNIT.", "SUBTOTAL"],
            [[str(numero), detalle.producto.nombre, str(detalle.cantidad),
              CLP.format(detalle.precio_unitario_congelado),
              CLP.format(detalle.calcular_subtotal())]
             for numero, detalle in enumerate(pedido.detalles, 1)],
            ["<", "<", ">", ">", ">"],
        )
        panel("TOTALES", [
            ("Subtotal productos", CLP.format(pedido.total_final_clp - pedido.total_flete_clp) + " CLP"),
            ("Flete", CLP.format(pedido.total_flete_clp) + " CLP"),
            ("TOTAL FINAL", CLP.format(pedido.total_final_clp) + " CLP"),
        ])

    def _confirmar_pedido(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        pedido.confirmar_pedido()
        ok(f"Pedido {pedido.id_pedido} confirmado: hay stock suficiente y el "
           f"cliente es valido. El stock aun no se descuenta (falta el pago).")

    def _registrar_pago(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        pedido.registrar_pago()
        for detalle in pedido.detalles:
            self._productos.actualizar_stock(
                detalle.producto.id_producto, detalle.producto.stock
            )
        self._pedidos.actualizar_estado(
            pedido.id_pedido, pedido.estado_pago, pedido.estado_entrega, pedido.total_final_clp
        )
        ok(f"Pago registrado. El pedido quedo {pedido.estado_pago} y el stock fue descontado.")
        tabla(
            ["PRODUCTO", "STOCK RESTANTE"],
            [[detalle.producto.nombre, str(detalle.producto.stock)] for detalle in pedido.detalles],
            ["<", ">"],
        )

    def _despachar_pedido(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        pedido.despachar(self._sesion)
        self._pedidos.actualizar_estado(
            pedido.id_pedido, pedido.estado_pago, pedido.estado_entrega, pedido.total_final_clp
        )
        ok(f"Pedido {pedido.id_pedido} despachado por {self._sesion.nombre} "
           f"({self._sesion.rol}).")

    def _procesar_entrega(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        subtitulo(f"ENTREGAS DEL PEDIDO {pedido.id_pedido} (comportamiento polimorfico)")
        for numero, resultado in enumerate(pedido.procesar_despacho_entregas(), 1):
            print(f"\n  {negrita(str(numero) + '.')} {resultado['producto']} "
                  f"{gris('[' + resultado['tipo'] + ']')}")
            print(f"     {resultado['mensaje']}")
            if resultado.get("enlace"):
                print(f"     Enlace de descarga: {azul(resultado['enlace'])}")
            if resultado.get("agenda"):
                print(f"     Agenda: {resultado['agenda']} | Direccion: {resultado['direccion']}")
        self._pedidos.actualizar_estado(
            pedido.id_pedido, pedido.estado_pago, pedido.estado_entrega, pedido.total_final_clp
        )

    def _eliminar_pedido(self) -> None:
        pedido = self._elegir_pedido()
        if pedido is None:
            return
        confirmar = pedir_opcion(
            f"  Confirma eliminar el pedido {pedido.id_pedido}? (1=Si, 0=No)",
            ["1", "0"], self._entrada,
        )
        if confirmar != "1":
            info("Operacion cancelada.")
            return
        if self._pedidos.eliminar(pedido.id_pedido):
            ok(f"Pedido {pedido.id_pedido} eliminado junto con sus lineas de detalle.")

    # ==================================================================
    # Indicador externo y RBAC
    # ==================================================================
    def _calcular_precio_dolar(self) -> None:
        subtitulo("PRECIO CON EL DOLAR DEL DIA (mindicador.cl con respaldo findic.cl)")
        valor = self._valor_dolar()
        if valor is None:
            info("El sistema continua funcionando: puede reintentar mas tarde.")
            return
        importados = self._productos.listar("ELECTRONICA")
        if not importados:
            aviso("No hay productos de electronica importada en el catalogo.")
            return
        tabla(
            ["CODIGO", "PRODUCTO", "USD", "CLP DEL DIA"],
            [[p.id_producto, p.nombre, f"{p.precio_usd:,.2f}",
              f"{p.calcular_precio_final(valor):,.0f}"] for p in importados],
            ["<", "<", ">", ">"],
        )
        info(f"Calculado con el dolar de hoy: ${valor:,.2f} CLP/USD")

    def _listar_trabajadores(self) -> None:
        subtitulo("TRABAJADORES Y PERMISOS (RBAC)")
        tabla(
            ["TRABAJADOR", "ROL", "MODIFICA CATALOGO", "DESPACHA"],
            [[t.nombre, t.rol, "Si" if t.puede_modificar_catalogo() else "No",
              "Si" if t.puede_despachar() else "No"] for t in self._trabajadores.listar()],
            ["<", "<", "<", "<"],
        )

    def _iniciar_sesion(self) -> None:
        subtitulo("INICIAR SESION")
        usuario = self._entrada("  Usuario (nombre o correo): ").strip()
        password = self._entrada("  Contrasena: ")
        autenticado = self._trabajadores.autenticar(usuario, password)
        self._sesion = autenticado
        ok(f"Bienvenido {autenticado.nombre} ({autenticado.rol}).")

    def _cargar_demo(self) -> None:
        cargar_datos_iniciales(self._bd)
        ok("Datos de demostracion cargados (solo se agregan si faltan).")


def main() -> None:
    try:
        AplicacionClickAndGo().ejecutar()
    except KeyboardInterrupt:
        print("\n\n  Ejecucion interrumpida por el usuario.\n")
    except ClickAndGoError as error:
        print(f"\n  [!] No se pudo iniciar el sistema: {error}\n")
    except sqlite3.Error as error:
        print(f"\n  [!] Error de base de datos al iniciar: {error}\n")


if __name__ == "__main__":
    main()
