#!/usr/bin/env python3
"""Pruebas automatizadas del Guion de Pruebas (P01 a P19).

Ejecutar desde la raiz del repositorio:

    python tests/test_guion_pruebas.py

Cada prueba replica un caso del archivo
"05 - E-commerce - Guion de pruebas(Guion de pruebas).csv".

Desde la mejora de la Sumativa N3 los codigos de clientes y productos son
automaticos, por lo que las pruebas seleccionan los registros por su codigo
generado (C01, F01, D01, S01, E01) o por su numero en la lista.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dao.conexion import ConexionBD  # noqa: E402
from main import AplicacionClickAndGo  # noqa: E402
from servicios.codigos import GeneradorCodigos  # noqa: E402
from servicios.indicador_dolar import ServicioIndicadorDolar  # noqa: E402
from servicios.inicializacion import cargar_datos_iniciales, preparar_base  # noqa: E402


class EntradaGuion:
    """Simula el teclado entregando una secuencia fija de respuestas."""

    def __init__(self, respuestas: list[str]) -> None:
        self._respuestas = list(respuestas)

    def __call__(self, mensaje: str = "") -> str:
        if not self._respuestas:
            raise AssertionError(f"El guion no tiene mas respuestas (pidio: {mensaje!r})")
        return self._respuestas.pop(0)


class BaseGuion(unittest.TestCase):
    def setUp(self) -> None:
        self._temporal = tempfile.TemporaryDirectory()
        self.ruta_bd = Path(self._temporal.name) / "pruebas.db"
        self._contador = 0

    def tearDown(self) -> None:
        self._temporal.cleanup()

    def ejecutar_app(self, respuestas: list[str]) -> str:
        self._contador += 1
        app = AplicacionClickAndGo(
            ConexionBD(self.ruta_bd), entrada=EntradaGuion(respuestas), color=False
        )
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            app.ejecutar()
        self._contador -= 1
        return salida.getvalue()

    # ------------------------------------------------------------------
    # P01: ejecucion y menu
    # ------------------------------------------------------------------
    def test_p01_el_programa_se_ejecuta_y_muestra_menu(self) -> None:
        resultado = subprocess.run(
            [sys.executable, "main.py"],
            cwd=RAIZ,
            input="0\n",
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "CLICKANDGO_DB": str(self.ruta_bd), "CLICKANDGO_COLOR": "0"},
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("MENU PRINCIPAL", resultado.stdout)
        self.assertIn("Clientes", resultado.stdout)
        self.assertIn("Productos", resultado.stdout)

    def test_menu_muestra_la_pista_de_codigos_automaticos(self) -> None:
        salida = self.ejecutar_app(["0"])
        self.assertIn("codigos de clientes y productos se generan automaticamente", salida)

    # ------------------------------------------------------------------
    # Codigos automaticos (mejora de la Sumativa N3)
    # ------------------------------------------------------------------
    def test_codigos_automaticos_de_clientes_y_productos(self) -> None:
        conexion = ConexionBD(self.ruta_bd)
        preparar_base(conexion)
        cargar_datos_iniciales(conexion)
        generador = GeneradorCodigos(conexion)
        # Los datos iniciales usan C01/C02 y F01/D01/S01/E01.
        self.assertEqual(generador.siguiente_cliente(), "C03")
        self.assertEqual(generador.siguiente_producto("FISICO"), "F02")
        self.assertEqual(generador.siguiente_producto("DIGITAL"), "D02")
        self.assertEqual(generador.siguiente_producto("SERVICIO"), "S02")
        self.assertEqual(generador.siguiente_producto("ELECTRONICA"), "E02")
        self.assertEqual(generador.siguiente_pedido(), "PED-1001")

    def test_el_usuario_nunca_escribe_el_codigo(self) -> None:
        """Solo se piden nombre, tipo y datos; el codigo se muestra al final."""
        salida = self.ejecutar_app(["1", "1", "Cliente Nuevo", "2", "nuevo@correo.cl", "0", "0"])
        self.assertIn("El sistema asignara el codigo automaticamente", salida)
        self.assertIn("Codigo asignado", salida)
        self.assertIn("C03", salida)

    # ------------------------------------------------------------------
    # P02 a P06: CRUD de una entidad principal
    # ------------------------------------------------------------------
    def test_p02_p03_p04_p06_crud_producto(self) -> None:
        salida = self.ejecutar_app(
            [
                "2", "1",                 # crear producto
                "4",                      # electronica importada (precio en USD)
                "Audífonos", "3", "30", "0.5", "0.01", "12",
                "2",                      # listar catalogo
                "3", "E02", "", "5", "30",  # modificar stock a 5
                "2",                      # listar de nuevo
                "0", "0",
            ]
        )
        self.assertIn("PRODUCTO REGISTRADO", salida)
        self.assertIn("E02", salida)
        self.assertIn("Audífonos", salida)
        self.assertIn("PRODUCTO ACTUALIZADO", salida)
        self.assertIn("stock 5", salida)

        # P06: eliminar
        salida = self.ejecutar_app(["2", "4", "E02", "1", "2", "0", "0"])
        self.assertIn("eliminado del catalogo", salida)
        self.assertNotIn("Audífonos", salida.split("CATALOGO")[-1])

    def test_p05_los_datos_quedan_guardados(self) -> None:
        self.ejecutar_app(
            ["2", "1", "1", "Producto Persistente", "7", "15000", "1.0", "0.02", "0", "0"]
        )
        # "Cerrar" y volver a abrir el programa: la base de datos es la misma.
        salida = self.ejecutar_app(["2", "2", "0", "0"])
        self.assertIn("Producto Persistente", salida)
        self.assertIn("F02", salida)

    # ------------------------------------------------------------------
    # P07 y P08: dato obligatorio con validacion
    # ------------------------------------------------------------------
    def test_p07_p08_validacion_de_identificador(self) -> None:
        salida = self.ejecutar_app(
            [
                "1", "1", "Cliente Valido", "2", "cliente@correo.cl",
                "1", "1", "Cliente Invalido", "2", "cliente@", "cliente@correo.cl",
                "2",                      # listar clientes
                "0", "0",
            ]
        )
        self.assertIn("no es valido", salida)
        self.assertIn("Intente nuevamente", salida)
        self.assertIn("CLIENTE REGISTRADO", salida)

    # ------------------------------------------------------------------
    # P09 a P11: entrega polimorfica por tipo de producto
    # ------------------------------------------------------------------
    def _crear_catalogo_base(self, proxima_fecha: str) -> list[str]:
        return [
            # fisico -> F02
            "2", "1", "1", "Silla Ergonómica", "10", "85000", "14", "0.15", "0",
            # digital -> D02
            "2", "1", "2", "Licencia Antivirus", "50", "24990",
            "https://cdn.clickandgo.cl/antivirus.iso", "CKG-2026-X94B", "450",
            "0",
            # servicio -> S02
            "2", "1", "3", "Instalación Red", "15", "40000",
            proxima_fecha, "Av. Apoquindo 4500", "2", "0",
            # electronica -> E02
            "2", "1", "4", "Monitor 4K Importado", "5", "250", "4.5", "0.03", "12",
            "0",
        ]

    def test_p09_p10_p11_entrega_polimorfica(self) -> None:
        fecha = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
        respuestas = self._crear_catalogo_base(fecha)
        respuestas += [
            "3", "1", "C01",                       # crear pedido para el cliente demo
            "F02", "2", "D02", "1", "S02", "1", "0",
            "7", "PED-1001",                       # procesar entrega
            "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("DESPACHO_COURIER", salida)
        self.assertIn("DESCARGA_DIGITAL", salida)
        self.assertIn("SERVICIO_TECNICO", salida)
        self.assertIn("Flete calculado", salida)
        self.assertIn("Enlace de descarga", salida)
        self.assertIn("Servicio agendado para el", salida)

    # ------------------------------------------------------------------
    # P12 y P13: transaccion con lineas de detalle
    # ------------------------------------------------------------------
    def test_p12_p13_pedido_multilinea_y_detalle(self) -> None:
        fecha = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
        respuestas = self._crear_catalogo_base(fecha)
        respuestas += [
            "3", "1", "C01",
            "F02", "2", "E02", "1", "D02", "1", "0",
            "3", "PED-1001",
            "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("PEDIDO GUARDADO", salida)
        self.assertIn("Lineas de detalle", salida)
        self.assertIn("DETALLE DEL PEDIDO PED-1001", salida)
        self.assertIn("Silla Ergonómica", salida)
        self.assertIn("TOTAL FINAL", salida)

    # ------------------------------------------------------------------
    # P14 y P15: las dos reglas que impiden una operacion
    # ------------------------------------------------------------------
    def test_p14_regla_stock_insuficiente(self) -> None:
        respuestas = [
            "2", "1", "1", "Producto Escaso", "3", "10000", "1", "0.01",
            "0",
            "3", "1", "C01", "F02", "5", "0",
            "4", "PED-1001",              # confirmar -> debe fallar
            "2", "2",                     # listar pedidos y catalogo
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("Stock insuficiente", salida)
        self.assertIn("Operacion no realizada", salida)
        # El stock no cambio
        self.assertIn("stock 3", salida)

    def test_p15_regla_pedido_impago_no_se_despacha(self) -> None:
        respuestas = [
            "2", "1", "1", "Producto Pagable", "10", "10000", "1", "0.01",
            "0",
            "3", "1", "C01", "F02", "1", "0",
            "4", "PED-1001",              # confirmar (ok)
            "6", "PED-1001",              # despachar sin pago -> debe fallar
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("no puede despacharse", salida)
        self.assertIn("Operacion no realizada", salida)

    def test_tambien_bloquea_el_catalogo_sin_permisos(self) -> None:
        """El encargado de bodega no puede modificar el catalogo (RBAC)."""
        salida = self.ejecutar_app(
            [
                "6", "Juan Perez", "bodega1234",
                "2", "1", "1", "Producto Demo", "1", "1000", "1", "0.01",
                "0", "0",
            ]
        )
        self.assertIn("no tiene autorizacion para modificar el catalogo", salida)

    def test_pago_y_despacho_exitosos(self) -> None:
        respuestas = [
            "2", "1", "1", "Producto Pagable", "10", "10000", "1", "0.01",
            "0",
            "3", "1", "C01", "F02", "2", "0",
            "4", "PED-1001",              # confirmar
            "5", "PED-1001",              # pagar
            "6", "PED-1001",              # despachar
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("Pago registrado", salida)
        self.assertIn("STOCK RESTANTE", salida)
        self.assertIn("despachado por", salida)

    # ------------------------------------------------------------------
    # P16 y P17: indicador externo
    # ------------------------------------------------------------------
    def test_p16_precio_con_dolar_del_dia(self) -> None:
        servicio = ServicioIndicadorDolar(timeout=15.0)
        try:
            indicador = servicio.obtener_valor_dolar()
        except Exception as error:  # sin internet: se prueba con el respaldo
            self.skipTest(f"Sin conexion a mindicador.cl ({error})")
        self.assertGreater(indicador.valor, 0)
        self.assertIn("mindicador.cl", indicador.fuente)

    def test_p16_menu_calcula_el_precio_de_importados(self) -> None:
        salida = self.ejecutar_app(["4", "0"])
        if "No fue posible obtener el dolar" in salida:
            self.skipTest("Sin conexion a mindicador.cl")
        self.assertIn("Monitor 4K Importado", salida)
        self.assertIn("CLP DEL DIA", salida)

    def test_p17_sin_internet_el_programa_no_se_cae(self) -> None:
        servicio = ServicioIndicadorDolar(
            url="https://host-invalido.invalid/api/dolar",
            timeout=3.0,
            ruta_respaldo=Path(self._temporal.name) / "sin_respaldo.json",
        )
        indicador, advertencia = servicio.valor_para_calculo()
        self.assertIsNone(indicador)
        self.assertIsNotNone(advertencia)
        self.assertIn("No fue posible obtener el dolar", advertencia)

    def test_p17_menu_avisa_sin_internet(self) -> None:
        app = AplicacionClickAndGo(
            ConexionBD(self.ruta_bd), entrada=EntradaGuion(["4", "0"]), color=False
        )
        app._dolar = ServicioIndicadorDolar(  # noqa: SLF001
            url="https://host-invalido.invalid/api/dolar",
            timeout=3.0,
            ruta_respaldo=Path(self._temporal.name) / "sin_respaldo.json",
        )
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            app.ejecutar()
        self.assertIn("No fue posible obtener el dolar", salida.getvalue())
        self.assertIn("continua funcionando", salida.getvalue())

    # ------------------------------------------------------------------
    # P18 y P19: estabilidad ante entradas invalidas
    # ------------------------------------------------------------------
    def test_p18_opcion_de_menu_inexistente(self) -> None:
        salida = self.ejecutar_app(["99", "0"])
        self.assertIn("no existe", salida)
        self.assertIn("MENU PRINCIPAL", salida)

    def test_p19_letras_donde_va_un_numero(self) -> None:
        salida = self.ejecutar_app(
            [
                "2", "1", "1", "Producto Letras", "abc", "3",
                "10000", "1", "0.01",
                "0", "0",
            ]
        )
        self.assertIn("no es un numero entero valido", salida)
        self.assertIn("PRODUCTO REGISTRADO", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
