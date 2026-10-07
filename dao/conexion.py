"""Conexion segura a SQLite y creacion automatica del esquema.

Todas las consultas del proyecto se ejecutan con parametros enlazados
(``?`` / ``:nombre``); nunca se concatena texto escrito por el usuario.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_PREDETERMINADA = RUTA_PROYECTO / "datos" / "clickandgo.db"

ESQUEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS trabajadores (
    id_trabajador   TEXT PRIMARY KEY,
    nombre          TEXT NOT NULL,
    correo          TEXT NOT NULL,
    rol             TEXT NOT NULL CHECK (rol IN ('ADMINISTRADOR', 'ENCARGADO_BODEGA')),
    extra           TEXT,
    password_hash   TEXT NOT NULL,
    salt            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente          TEXT PRIMARY KEY,
    nombre              TEXT NOT NULL,
    identificador       TEXT NOT NULL,
    tipo_identificador  TEXT NOT NULL CHECK (tipo_identificador IN ('RUT', 'EMAIL'))
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto             TEXT PRIMARY KEY,
    tipo                    TEXT NOT NULL CHECK (tipo IN ('FISICO', 'ELECTRONICA', 'DIGITAL', 'SERVICIO')),
    nombre                  TEXT NOT NULL,
    precio_base_clp         REAL NOT NULL DEFAULT 0,
    precio_usd              REAL NOT NULL DEFAULT 0,
    stock                   INTEGER NOT NULL CHECK (stock >= 0),
    peso_kg                 REAL NOT NULL DEFAULT 0,
    volumen_m3              REAL NOT NULL DEFAULT 0,
    tarifa_flete_base       REAL NOT NULL DEFAULT 0,
    enlace_descarga         TEXT NOT NULL DEFAULT '',
    licencia_activacion     TEXT NOT NULL DEFAULT '',
    peso_archivo_mb         REAL NOT NULL DEFAULT 0,
    fecha_agendada          TEXT NOT NULL DEFAULT '',
    direccion_visita        TEXT NOT NULL DEFAULT '',
    duracion_estimada_horas INTEGER NOT NULL DEFAULT 0,
    garantia_meses          INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido        TEXT PRIMARY KEY,
    id_cliente       TEXT NOT NULL REFERENCES clientes(id_cliente),
    fecha_creacion   TEXT NOT NULL,
    estado_pago      TEXT NOT NULL CHECK (estado_pago IN ('PENDIENTE', 'PAGADO', 'RECHAZADO')),
    estado_entrega   TEXT NOT NULL CHECK (estado_entrega IN ('PENDIENTE', 'EN_PREPARACION', 'DESPACHADO', 'ENTREGADO')),
    total_flete_clp  REAL NOT NULL DEFAULT 0,
    total_final_clp  REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_detalle                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido                   TEXT NOT NULL REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    id_producto                 TEXT NOT NULL REFERENCES productos(id_producto),
    cantidad                    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario_congelado   REAL NOT NULL CHECK (precio_unitario_congelado >= 0),
    tipo_entrega                TEXT NOT NULL DEFAULT '',
    detalle_entrega             TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS configuracion (
    clave       TEXT PRIMARY KEY,
    valor       TEXT NOT NULL,
    actualizado TEXT NOT NULL
);
"""


class _ConexionAdministrada:
    """Envoltorio que garantiza el cierre de la conexion SQLite.

    ``sqlite3.Connection`` usado como context manager hace commit/rollback,
    pero no cierra el archivo. Este envoltorio agrega el ``close()`` para no
    dejar descriptores abiertos cuando el programa corre muchas consultas.
    """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def __enter__(self) -> sqlite3.Connection:
        return self._conexion

    def __exit__(self, tipo, valor, traza) -> bool:
        try:
            if tipo is None:
                self._conexion.commit()
            else:
                self._conexion.rollback()
        finally:
            self._conexion.close()
        return False

    def __getattr__(self, nombre):
        return getattr(self._conexion, nombre)


class ConexionBD:
    """Administra la conexion y las sentencias parametrizadas."""

    def __init__(self, ruta: str | os.PathLike | None = None) -> None:
        ruta = ruta or os.environ.get("CLICKANDGO_DB") or RUTA_PREDETERMINADA
        self._ruta = Path(ruta)
        if str(self._ruta) != ":memory:":
            self._ruta.parent.mkdir(parents=True, exist_ok=True)

    @property
    def ruta(self) -> Path:
        return self._ruta

    def conectar(self) -> "_ConexionAdministrada":
        conexion = sqlite3.connect(str(self._ruta))
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON;")
        return _ConexionAdministrada(conexion)

    def crear_tablas(self) -> None:
        with self.conectar() as conexion:
            conexion.executescript(ESQUEMA)

    # ------------------------------------------------------------------
    # Helpers de consulta parametrizada
    # ------------------------------------------------------------------
    def ejecutar(self, sql: str, parametros: dict | tuple = ()) -> int:
        conexion = self.conectar()
        try:
            cursor = conexion.execute(sql, parametros)
            conexion.commit()
            return cursor.lastrowid
        finally:
            conexion.close()

    def ejecutar_muchos(self, sql: str, filas: list[dict | tuple]) -> None:
        conexion = self.conectar()
        try:
            conexion.executemany(sql, filas)
            conexion.commit()
        finally:
            conexion.close()

    def consultar(self, sql: str, parametros: dict | tuple = ()) -> list[sqlite3.Row]:
        conexion = self.conectar()
        try:
            return conexion.execute(sql, parametros).fetchall()
        finally:
            conexion.close()

    def consultar_uno(self, sql: str, parametros: dict | tuple = ()) -> sqlite3.Row | None:
        conexion = self.conectar()
        try:
            return conexion.execute(sql, parametros).fetchone()
        finally:
            conexion.close()

    def guardar_configuracion(self, clave: str, valor: str) -> None:
        from datetime import datetime

        self.ejecutar(
            """
            INSERT INTO configuracion (clave, valor, actualizado)
            VALUES (:clave, :valor, :actualizado)
            ON CONFLICT(clave) DO UPDATE SET valor = :valor, actualizado = :actualizado
            """,
            {
                "clave": clave,
                "valor": valor,
                "actualizado": datetime.now().isoformat(timespec="seconds"),
            },
        )

    def leer_configuracion(self, clave: str) -> str | None:
        fila = self.consultar_uno(
            "SELECT valor FROM configuracion WHERE clave = :clave", {"clave": clave}
        )
        return fila["valor"] if fila else None
