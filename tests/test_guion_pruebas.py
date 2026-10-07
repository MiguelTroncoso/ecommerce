#!/usr/bin/env python3
"""Pruebas automatizadas del Guion de Pruebas (P01 a P19).

Ejecutar desde la raiz del repositorio:

    python tests/test_guion_pruebas.py

Cada prueba replica un caso del archivo
"05 - E-commerce - Guion de pruebas(Guion de pruebas).csv".
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
from model.excepciones import PedidoNoPagadoError, StockInsuficienteError  # noqa: E402
from servicios.indicador_dolar import ServicioIndicadorDolar  # noqa: E402


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

    def tearDown(self) -> None:
        self._temporal.cleanup()

    def ejecutar_app(self, respuestas: list[str]) -> str:
        app = AplicacionClickAndGo(ConexionBD(self.ruta_bd), entrada=EntradaGuion(respuestas))
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            app.ejecutar()
        return salida.getvalue()

    # ------------------------------------------------------------------
    # P01 a P06: CRUD de una entidad principal
    # ------------------------------------------------------------------
    def test_p01_el_programa_se_ejecuta_y_muestra_menu(self) -> None:
        resultado = subprocess.run(
            [sys.executable, "main.py"],
            cwd=RAIZ,
            input="0\n",
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "CLICKANDGO_DB": str(self.ruta_bd)},
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("MENU PRINCIPAL", resultado.stdout)
        self.assertIn("1. Gestionar clientes", resultado.stdout)

    def test_p02_p03_p04_p06_crud_producto(self) -> None:
        salida = self.ejecutar_app(
            [
                "2", "1",            # crear producto
                "4",                 # electronica importada (precio USD)
                "PROD-T01", "Audífonos", "3", "30", "0.5", "0.01", "12",
                "2",                 # listar catalogo
                "3", "PROD-T01", "", "5", "30",   # modificar stock a 5
                "2",                 # listar de nuevo
                "0",                 # volver
                "0",                 # salir
            ]
        )
        self.assertIn("[OK] Producto guardado", salida)
        self.assertIn("Audífonos", salida)
        self.assertIn("stock 5", salida)
        self.assertIn("PROD-T01", salida)

        # P06: eliminar
        salida = self.ejecutar_app(["2", "4", "PROD-T01", "2", "0", "0"])
        self.assertIn("eliminado del catalogo", salida)
        catalogo = salida.split("CATALOGO")[-1]
        self.assertNotIn("PROD-T01", catalogo)

    def test_p05_los_datos_quedan_guardados(self) -> None:
        self.ejecutar_app(
            ["2", "1", "1", "PROD-P05", "Producto Persistente", "7", "15000", "1.0", "0.02", "0", "0"]
        )
        # "Cerrar" y volver a abrir el programa: la base de datos es la misma.
        salida = self.ejecutar_app(["2", "2", "0", "0"])
        self.assertIn("Producto Persistente", salida)

    # ------------------------------------------------------------------
    # P07 y P08: dato obligatorio con validacion
    # ------------------------------------------------------------------
    def test_p07_p08_validacion_de_identificador(self) -> None:
        salida = self.ejecutar_app(
            [
                "1", "1", "CLI-T01", "Cliente Valido", "2", "cliente@correo.cl",
                "1", "1", "CLI-T02", "Cliente Invalido", "2", "cliente@", "cliente@correo.cl",
                "0", "0", "0",
            ]
        )
        self.assertIn("no es valido", salida)
        self.assertIn("[OK] Cliente guardado", salida)
        self.assertIn("Intente nuevamente", salida)

    # ------------------------------------------------------------------
    # P09 a P11: entrega polimorfica por tipo de producto
    # ------------------------------------------------------------------
    def _crear_catalogo_base(self, proxima_fecha: str) -> list[str]:
        return [
            # fisico
            "2", "1", "1", "PROD-FIS", "Silla Ergonómica", "10", "85000", "14", "0.15",
            # digital
            "2", "1", "2", "PROD-DIG", "Licencia Antivirus", "50", "24990",
            "https://cdn.clickandgo.cl/antivirus.iso", "CKG-2026-X94B", "450",
            # servicio
            "2", "1", "3", "PROD-SER", "Instalación Red", "15", "40000",
            proxima_fecha, "Av. Apoquindo 4500", "2",
            # electronica
            "2", "1", "4", "PROD-ELE", "Monitor 4K Importado", "5", "250", "4.5", "0.03", "12",
            "0",
        ]

    def test_p09_p10_p11_entrega_polimorfica(self) -> None:
        fecha = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
        respuestas = self._crear_catalogo_base(fecha)
        respuestas += [
            "3", "1", "CLI-01", "",                       # pedido con cliente demo
            "PROD-FIS", "2", "PROD-DIG", "1", "PROD-SER", "1", "fin",
            "7", "PED-1001",                               # procesar entrega
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("DESPACHO_COURIER", salida)
        self.assertIn("DESCARGA_DIGITAL", salida)
        self.assertIn("SERVICIO_TECNICO", salida)
        self.assertIn("Flete calculado", salida)
        self.assertIn("Licencia: CKG-2026-X94B", salida)
        self.assertIn("Servicio agendado para el", salida)

    # ------------------------------------------------------------------
    # P12 y P13: transaccion con lineas de detalle
    # ------------------------------------------------------------------
    def test_p12_p13_pedido_multilinea_y_detalle(self) -> None:
        fecha = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
        respuestas = self._crear_catalogo_base(fecha)
        respuestas += [
            "3", "1", "CLI-01", "",
            "PROD-FIS", "2", "PROD-ELE", "1", "PROD-DIG", "1", "fin",
            "3", "PED-1001",
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("Pedido guardado con 3 linea(s)", salida)
        self.assertIn("DETALLE DEL PEDIDO PED-1001", salida)
        self.assertIn("2 x Silla Ergonómica", salida)

    # ------------------------------------------------------------------
    # P14 y P15: las dos reglas que impiden una operacion
    # ------------------------------------------------------------------
    def test_p14_regla_stock_insuficiente(self) -> None:
        respuestas = [
            "2", "1", "1", "PROD-STK", "Producto Escaso", "3", "10000", "1", "0.01", "0",
            "3", "1", "CLI-01", "", "PROD-STK", "5", "fin",
            "4", "PED-1001",          # confirmar -> debe fallar
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("Stock insuficiente", salida)
        self.assertIn("Operacion no realizada", salida)
        # El stock no cambio
        self.assertIn("stock 3", self.ejecutar_app(["2", "2", "0", "0"]))

    def test_p15_regla_pedido_impago_no_se_despacha(self) -> None:
        respuestas = [
            "2", "1", "1", "PROD-PAG", "Producto Pagable", "10", "10000", "1", "0.01", "0",
            "3", "1", "CLI-01", "", "PROD-PAG", "1", "fin",
            "4", "PED-1001",          # confirmar (ok)
            "6", "PED-1001",          # despachar sin pago -> debe fallar
            "0", "0", "0",
        ]
        salida = self.ejecutar_app(respuestas)
        self.assertIn("no puede despacharse", salida)
        self.assertIn("Operacion no realizada", salida)

    def test_tambien_bloquea_despacho_sin_permisos(self) -> None:
        """El encargado de bodega no puede modificar el catalogo (RBAC)."""
        salida = self.ejecutar_app(
            [
                "6", "Juan Perez", "bodega1234",
                "2", "1", "1", "PROD-X", "Producto Demo", "1", "1000", "1", "0.01",
                "0", "0", "0",
            ]
        )
        self.assertIn("no tiene autorizacion para modificar el catalogo", salida)

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
        app = AplicacionClickAndGo(ConexionBD(self.ruta_bd), entrada=EntradaGuion(["4", "0"]))
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
                "2", "1", "1", "PROD-LET", "Producto Letras", "abc", "3",
                "10000", "1", "0.01",
                "0", "0",
            ]
        )
        self.assertIn("no es un numero entero valido", salida)
        self.assertIn("[OK] Producto guardado", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
