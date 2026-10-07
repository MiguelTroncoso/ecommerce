#!/usr/bin/env python3
"""ClickAndGo 2.0 - Sistema de gestion e-commerce por consola.

Evaluacion Sumativa N2 - Programacion Orientada a Objeto Seguro (INACAP TI3V21)

Arquitectura:

    model/      clases del diagrama UML (una por archivo, con herencia,
                encapsulamiento y excepciones propias de negocio)
    dao/        persistencia SQLite con consultas parametrizadas
    servicios/  validacion de entradas y consumo de la API mindicador.cl
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
from servicios.indicador_dolar import ServicioIndicadorDolar  # noqa: E402
from servicios.inicializacion import cargar_datos_iniciales, preparar_base  # noqa: E402
from servicios.validador import (  # noqa: E402
    pedir_decimal,
    pedir_entero,
    pedir_fecha_futura,
    pedir_identificador,
    pedir_opcion,
    pedir_texto,
    pedir_url,
)

ANCHO = 78
CLP = "${:,.0f}"


def titulo(texto: str) -> None:
    print("\n" + "=" * ANCHO)
    print(f"  {texto}")
    print("=" * ANCHO)


def subtitulo(texto: str) -> None:
    print("\n" + "-" * ANCHO)
    print(f"  {texto}")
    print("-" * ANCHO)


class AplicacionClickAndGo:
    """Menu principal del sistema. ``entrada`` permite inyectar otro origen."""

    def __init__(self, conexion: ConexionBD | None = None, entrada=input) -> None:
        self._entrada = entrada
        self._bd = conexion or ConexionBD()
        self._clientes = ClienteDAO(self._bd)
        self._productos = ProductoDAO(self._bd)
        self._pedidos = PedidoDAO(self._bd)
        self._trabajadores = TrabajadorDAO(self._bd)
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
                print(f"\n  [!] Operacion no realizada: {error}")
            except sqlite3.IntegrityError as error:
                print(f"\n  [!] El registro no se pudo guardar: {error}")
            except (ValueError, TypeError) as error:
                print(f"\n  [!] Dato invalido: {error}")
            except KeyboardInterrupt:
                print("\n\n  Sesion finalizada por el usuario (Ctrl+C).")
                self._activo = False
            except Exception as error:  # red de seguridad: informa y continua
                print(f"\n  [!] Error inesperado controlado: {type(error).__name__}: {error}")

    @staticmethod
    def _opciones_menu() -> list[str]:
        return ["1", "2", "3", "4", "5", "6", "7", "0"]

    def _bienvenida(self) -> None:
        print("=" * ANCHO)
        print("   ClickAndGo  |  Sistema de gestion e-commerce")
        print("   INACAP TI3V21 - Evaluacion Sumativa N2 (POO Seguro)")
        print("=" * ANCHO)
        print(f"   Base de datos : {self._bd.ruta}")
        print(f"   Operador      : {self._sesion.nombre} ({self._sesion.rol})")
        print("=" * ANCHO)
        print("   Credenciales de demostracion:")
        print("     Administrador      -> usuario 'Maria Gonzalez'  / clave 'admin1234'")
        print("     Encargado de bodega -> usuario 'Juan Perez'     / clave 'bodega1234'")

    def _mostrar_menu(self) -> None:
        titulo("MENU PRINCIPAL")
        print("  1. Gestionar clientes")
        print("  2. Gestionar productos (catalogo)")
        print("  3. Gestionar pedidos (transacciones)")
        print("  4. Calcular precio con el dolar del dia (mindicador.cl)")
        print("  5. Ver trabajadores y permisos (RBAC)")
        print("  6. Iniciar sesion / cambiar operador")
        print("  7. Cargar datos de demostracion")
        print("  0. Salir")
        print(f"\n  Sesion activa: {self._sesion.nombre} ({self._sesion.rol})")

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
    # Clientes
    # ==================================================================
    def _menu_clientes(self) -> None:
        while True:
            subtitulo("CLIENTES")
            print("  1. Crear cliente (valida RUT Modulo 11 o correo)")
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
        subtitulo("NUEVO CLIENTE")
        id_cliente = pedir_texto("  Identificador interno (ej: CLI-03)", self._entrada, 2, 20)
        nombre = pedir_texto("  Nombre completo", self._entrada, 3, 80)
        tipo = pedir_opcion("  Tipo de identificador (1=RUT, 2=EMAIL)", ["1", "2"], self._entrada)
        if tipo is None:
            return
        tipo = "RUT" if tipo == "1" else "EMAIL"
        identificador = pedir_identificador(
            "  RUT (ej: 19.876.543-0)" if tipo == "RUT" else "  Correo (ej: cliente@correo.cl)",
            tipo,
            self._entrada,
        )
        cliente = Cliente(id_cliente, nombre, identificador, tipo)
        self._clientes.crear(cliente)
        print(f"\n  [OK] Cliente guardado: {cliente}")

    def _listar_clientes(self) -> None:
        subtitulo("LISTADO DE CLIENTES")
        clientes = self._clientes.listar()
        if not clientes:
            print("  No hay clientes registrados.")
            return
        for cliente in clientes:
            print(f"  - {cliente.id_cliente:<10} {cliente.nombre:<28} "
                  f"{cliente.tipo_identificador:<6} {cliente.identificador}")

    def _modificar_cliente(self) -> None:
        self._listar_clientes()
        id_cliente = pedir_texto("  Identificador interno a modificar", self._entrada, 2, 20)
        cliente = self._clientes.obtener(id_cliente)
        cliente.nombre = pedir_texto("  Nuevo nombre", self._entrada, 3, 80)
        tipo = pedir_opcion("  Tipo de identificador (1=RUT, 2=EMAIL)", ["1", "2"], self._entrada)
        if tipo is None:
            return
        tipo = "RUT" if tipo == "1" else "EMAIL"
        cliente.tipo_identificador = tipo
        cliente.identificador = pedir_identificador("  Nuevo identificador", tipo, self._entrada)
        self._clientes.actualizar(cliente)
        print(f"\n  [OK] Cliente actualizado: {cliente}")

    def _eliminar_cliente(self) -> None:
        self._listar_clientes()
        id_cliente = pedir_texto("  Identificador interno a eliminar", self._entrada, 2, 20)
        confirmar = pedir_opcion("  Confirma la eliminacion? (1=Si, 0=No)", ["1", "0"], self._entrada)
        if confirmar != "1":
            print("  Operacion cancelada.")
            return
        if self._clientes.eliminar(id_cliente):
            print(f"\n  [OK] Cliente {id_cliente} eliminado.")
        else:
            print(f"\n  [!] No existe el cliente {id_cliente}.")

    # ==================================================================
    # Productos
    # ==================================================================
    def _menu_productos(self) -> None:
        while True:
            subtitulo("CATALOGO DE PRODUCTOS")
            print("  1. Crear producto")
            print("  2. Listar productos")
            print("  3. Modificar producto (nombre / precio / stock)")
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
        subtitulo("NUEVO PRODUCTO")
        print("  Tipos disponibles:")
        print("   1 = Producto fisico (precio en CLP)")
        print("   2 = Producto digital (enlace de descarga)")
        print("   3 = Servicio tecnico (agenda futura)")
        print("   4 = Electronica importada (precio en USD)")
        tipo = pedir_opcion("  Tipo", ["1", "2", "3", "4"], self._entrada)
        if tipo is None:
            return
        id_producto = pedir_texto("  Identificador (ej: PROD-F02)", self._entrada, 2, 20)
        nombre = pedir_texto("  Nombre", self._entrada, 3, 60)
        stock = pedir_entero("  Stock inicial", self._entrada, 0, 1_000_000)
        producto = None

        if tipo == "1":
            precio = pedir_decimal("  Precio base CLP", self._entrada, 0)
            peso = pedir_decimal("  Peso en kg", self._entrada, 0.001)
            volumen = pedir_decimal("  Volumen en m3", self._entrada, 0.0001)
            producto = ProductoFisico(id_producto, nombre, precio, stock, peso, volumen)
        elif tipo == "2":
            precio = pedir_decimal("  Precio base CLP", self._entrada, 0)
            enlace = pedir_url("  Enlace de descarga", self._entrada)
            licencia = pedir_texto("  Licencia de activacion", self._entrada, 4, 40)
            peso_mb = pedir_decimal("  Peso del archivo en MB", self._entrada, 0)
            producto = ProductoDigital(id_producto, nombre, precio, stock, enlace, licencia, peso_mb)
        elif tipo == "3":
            precio = pedir_decimal("  Precio base CLP", self._entrada, 0)
            fecha = pedir_fecha_futura("  Fecha y hora (AAAA-MM-DD HH:MM)", self._entrada)
            direccion = pedir_texto("  Direccion de la visita", self._entrada, 5, 80)
            duracion = pedir_entero("  Duracion estimada en horas", self._entrada, 1, 24)
            producto = ProductoServicio(id_producto, nombre, precio, stock, fecha, direccion, duracion)
        else:
            precio_usd = pedir_decimal("  Precio en USD", self._entrada, 0.01)
            peso = pedir_decimal("  Peso en kg", self._entrada, 0.001)
            volumen = pedir_decimal("  Volumen en m3", self._entrada, 0.0001)
            garantia = pedir_entero("  Garantia en meses", self._entrada, 0, 120)
            producto = ProductoElectronica(
                id_producto, nombre, precio_usd, stock, peso, volumen, garantia
            )

        self._productos.crear(producto)
        print(f"\n  [OK] Producto guardado: {producto}")

    def _listar_productos(self, tipo: str | None = None) -> list:
        subtitulo("CATALOGO" + (f" - {tipo}" if tipo else ""))
        productos = self._productos.listar(tipo)
        if not productos:
            print("  No hay productos registrados.")
            return []
        for producto in productos:
            precio = f"USD {producto.precio_usd:,.2f}" if isinstance(
                producto, ProductoElectronica
            ) else f"${producto.precio_base_clp:,.0f} CLP"
            print(f"  - {producto.id_producto:<10} {producto.tipo:<12} "
                  f"{producto.nombre:<28} {precio:<16} stock {producto.stock}")
        return productos

    def _modificar_producto(self) -> None:
        self._validar_permiso_catalogo()
        productos = self._listar_productos()
        if not productos:
            return
        id_producto = pedir_texto("  Identificador del producto a modificar", self._entrada, 2, 20)
        producto = self._productos.obtener(id_producto)
        print(f"  Producto seleccionado: {producto}")
        nuevo_nombre = pedir_texto(
            f"  Nuevo nombre (Enter para mantener '{producto.nombre}')",
            self._entrada,
            3,
            60,
            permitir_vacio=True,
        )
        if nuevo_nombre:
            producto.nombre = nuevo_nombre
        nuevo_stock = pedir_entero(
            f"  Nuevo stock (actual {producto.stock})", self._entrada, 0, 1_000_000
        )
        producto.stock = nuevo_stock
        if isinstance(producto, ProductoElectronica):
            producto.precio_usd = pedir_decimal(
                f"  Nuevo precio USD (actual {producto.precio_usd})", self._entrada, 0.01
            )
        else:
            producto.precio_base_clp = pedir_decimal(
                f"  Nuevo precio CLP (actual {producto.precio_base_clp:,.0f})",
                self._entrada,
                0,
            )
        self._productos.actualizar(producto)
        print(f"\n  [OK] Producto actualizado: {producto}")

    def _eliminar_producto(self) -> None:
        self._validar_permiso_catalogo()
        productos = self._listar_productos()
        if not productos:
            return
        id_producto = pedir_texto("  Identificador del producto a eliminar", self._entrada, 2, 20)
        if self._productos.eliminar(id_producto):
            print(f"\n  [OK] Producto {id_producto} eliminado del catalogo.")
        else:
            print(f"\n  [!] No existe el producto {id_producto}.")

    # ==================================================================
    # Pedidos
    # ==================================================================
    def _menu_pedidos(self) -> None:
        while True:
            subtitulo("PEDIDOS")
            print("  1. Crear pedido (multi-linea)")
            print("  2. Listar pedidos")
            print("  3. Ver detalle de un pedido")
            print("  4. Confirmar pedido (Regla 1: stock suficiente)")
            print("  5. Registrar pago del pedido")
            print("  6. Despachar pedido (Regla 2: pedido pagado)")
            print("  7. Procesar entrega polimorfica")
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

    def _siguiente_id_pedido(self) -> str:
        numero = self._pedidos.contar() + 1001
        while True:
            candidato = f"PED-{numero}"
            if not self._pedidos._bd.consultar_uno(  # noqa: SLF001
                "SELECT 1 FROM pedidos WHERE id_pedido = :id", {"id": candidato}
            ):
                return candidato
            numero += 1

    def _valor_dolar(self) -> float | None:
        """Obtiene el dolar del dia informando cualquier falla."""
        self._dolar_consultado = True
        indicador, advertencia = self._dolar.valor_para_calculo()
        if advertencia:
            print(f"\n  [!] {advertencia}")
        if indicador is None:
            print("  [!] Sin valor de dolar disponible: no es posible cotizar importados.")
            return None
        self._valor_dolar_ultimo = indicador.valor
        print(f"  [i] Dolar utilizado: {indicador}")
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
        clientes = self._clientes.listar()
        if not clientes:
            print("  [!] Primero debe registrar al menos un cliente.")
            return
        for cliente in clientes:
            print(f"  {cliente.id_cliente:<10} {cliente.nombre}")
        id_cliente = pedir_texto("  Identificador del cliente", self._entrada, 2, 20)
        cliente = self._clientes.obtener(id_cliente)
        id_sugerido = self._siguiente_id_pedido()
        id_pedido = pedir_texto(
            f"  Numero de pedido (Enter para {id_sugerido})",
            self._entrada,
            4,
            20,
            permitir_vacio=True,
        ) or id_sugerido
        pedido = Pedido(id_pedido, cliente)

        while True:
            self._listar_productos()
            id_producto = pedir_texto(
                "  Producto a agregar (escriba FIN para terminar)", self._entrada, 1, 20
            )
            if id_producto.lower() in ("fin", "salir", "0"):
                break
            try:
                producto = self._productos.obtener(id_producto)
            except RegistroNoEncontradoError as error:
                print(f"  [!] {error}")
                continue
            cantidad = pedir_entero("  Cantidad", self._entrada, 1, 100000)
            valor_dolar = None
            if producto.tipo == "ELECTRONICA":
                valor_dolar = self._valor_dolar_si_falta()
                if valor_dolar is None:
                    print("  [!] Sin valor del dolar no se puede cotizar este producto importado.")
                    continue
            detalle = pedido.agregar_linea(producto, cantidad, valor_dolar)
            print(f"  [OK] Linea agregada: {detalle}")

        if not pedido.detalles:
            print("\n  [!] El pedido quedo sin lineas: no se guarda.")
            return
        self._pedidos.crear(pedido)
        print(f"\n  [OK] Pedido guardado con {len(pedido.detalles)} linea(s) de detalle.")
        print(f"       Total del pedido: {CLP.format(pedido.total_final_clp)} CLP "
              f"(flete {CLP.format(pedido.total_flete_clp)})")

    def _listar_pedidos(self) -> list:
        subtitulo("PEDIDOS REGISTRADOS")
        pedidos = self._pedidos.listar()
        if not pedidos:
            print("  No hay pedidos registrados.")
            return []
        for pedido in pedidos:
            print(f"  - {pedido}")
        return pedidos

    def _pedir_pedido(self) -> Pedido | None:
        self._listar_pedidos()
        id_pedido = pedir_texto("  Numero de pedido", self._entrada, 4, 20)
        return self._pedidos.obtener(id_pedido)

    def _ver_detalle_pedido(self) -> None:
        pedido = self._pedir_pedido()
        if pedido is None:
            return
        subtitulo(f"DETALLE DEL PEDIDO {pedido.id_pedido}")
        print(f"  Cliente        : {pedido.cliente.nombre} ({pedido.cliente.identificador})")
        print(f"  Fecha          : {pedido.fecha_creacion:%Y-%m-%d %H:%M}")
        print(f"  Estado de pago : {pedido.estado_pago}")
        print(f"  Estado entrega : {pedido.estado_entrega}")
        print("  Lineas de detalle:")
        for numero, detalle in enumerate(pedido.detalles, 1):
            print(f"    {numero}. {detalle}  -> ${detalle.calcular_subtotal():,.0f} CLP")
        print(f"  Flete total    : {CLP.format(pedido.total_flete_clp)} CLP")
        print(f"  TOTAL FINAL    : {CLP.format(pedido.total_final_clp)} CLP")

    def _confirmar_pedido(self) -> None:
        pedido = self._pedir_pedido()
        if pedido is None:
            return
        pedido.confirmar_pedido()
        print(f"\n  [OK] El pedido {pedido.id_pedido} fue confirmado: hay stock suficiente "
              f"y el cliente es valido. El stock aun no se descuenta (falta el pago).")

    def _registrar_pago(self) -> None:
        pedido = self._pedir_pedido()
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
        print(f"\n  [OK] Pago registrado. El pedido figura como {pedido.estado_pago} "
              f"y el stock fue descontado.")

    def _despachar_pedido(self) -> None:
        pedido = self._pedir_pedido()
        if pedido is None:
            return
        pedido.despachar(self._sesion)
        self._pedidos.actualizar_estado(
            pedido.id_pedido, pedido.estado_pago, pedido.estado_entrega, pedido.total_final_clp
        )
        print(f"\n  [OK] Pedido {pedido.id_pedido} despachado por "
              f"{self._sesion.nombre} ({self._sesion.rol}).")

    def _procesar_entrega(self) -> None:
        pedido = self._pedir_pedido()
        if pedido is None:
            return
        subtitulo(f"ENTREGAS DEL PEDIDO {pedido.id_pedido} (comportamiento polimorfico)")
        for numero, resultado in enumerate(pedido.procesar_despacho_entregas(), 1):
            print(f"  {numero}. [{resultado['tipo']}] {resultado['producto']}")
            print(f"     {resultado['mensaje']}")
            if resultado.get("enlace"):
                print(f"     Enlace de descarga: {resultado['enlace']}")
            if resultado.get("agenda"):
                print(f"     Agenda: {resultado['agenda']} | Direccion: {resultado['direccion']}")
        self._pedidos.actualizar_estado(
            pedido.id_pedido, pedido.estado_pago, pedido.estado_entrega, pedido.total_final_clp
        )

    def _eliminar_pedido(self) -> None:
        pedido = self._pedir_pedido()
        if pedido is None:
            return
        confirmar = pedir_opcion("  Confirma la eliminacion? (1=Si, 0=No)", ["1", "0"], self._entrada)
        if confirmar != "1":
            print("  Operacion cancelada.")
            return
        if self._pedidos.eliminar(pedido.id_pedido):
            print(f"\n  [OK] Pedido {pedido.id_pedido} eliminado (con sus lineas de detalle).")

    # ==================================================================
    # Indicador externo y RBAC
    # ==================================================================
    def _calcular_precio_dolar(self) -> None:
        subtitulo("PRECIO CON EL DOLAR DEL DIA (mindicador.cl)")
        valor = self._valor_dolar()
        if valor is None:
            print("  El sistema continua funcionando: puede reintentar mas tarde.")
            return
        importados = self._productos.listar("ELECTRONICA")
        if not importados:
            print("  No hay productos de electronica importada en el catalogo.")
            return
        print(f"\n  {'PRODUCTO':<28}{'USD':>10}{'CLP DEL DIA':>18}")
        print("  " + "-" * 56)
        for producto in importados:
            precio_clp = producto.calcular_precio_final(valor)
            print(f"  {producto.nombre:<28}{producto.precio_usd:>10,.2f}{precio_clp:>18,.0f}")
            print(f"     (USD {producto.precio_usd:,.2f} x {valor:,.2f} = ${precio_clp:,.0f} CLP, "
                  f"stock {producto.stock})")

    def _listar_trabajadores(self) -> None:
        subtitulo("TRABAJADORES Y PERMISOS (RBAC)")
        for trabajador in self._trabajadores.listar():
            print(f"  - {trabajador.nombre:<18} {trabajador.rol:<18} "
                  f"modificar_catalogo={trabajador.puede_modificar_catalogo()!s:<5} "
                  f"despachar={trabajador.puede_despachar()}")

    def _iniciar_sesion(self) -> None:
        subtitulo("INICIAR SESION")
        usuario = self._entrada("  Usuario (nombre o correo): ").strip()
        password = self._entrada("  Contrasena: ")
        autenticado = self._trabajadores.autenticar(usuario, password)
        self._sesion = autenticado
        print(f"\n  [OK] Bienvenido {autenticado.nombre} ({autenticado.rol}).")

    def _cargar_demo(self) -> None:
        cargar_datos_iniciales(self._bd)
        print("\n  [OK] Datos de demostracion cargados (solo se agregan si faltan).")


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
