#!/usr/bin/env python3
"""Sitio web de ClickAndGo: documentacion y consola en vivo.

Publica el proyecto en https://inacap.superflash.site con dos objetivos:

1. Presentar el proyecto al cliente desde cero (arquitectura, decisiones de
   seguridad, recorrido del codigo y resultados del guion de pruebas).
2. Permitir una demostracion en linea: cada visitante obtiene una sesion
   aislada que ejecuta el mismo ``main.py`` en un pseudo-terminal.

Ejecucion local:

    python web/app.py
Produccion:

    waitress-serve --listen=127.0.0.1:3030 web.app:app
"""

from __future__ import annotations

import fcntl
import os
import pty
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

RAIZ = Path(__file__).resolve().parent.parent
DIR_DOCS = RAIZ / "docs"
DIR_DATOS_WEB = Path(os.environ.get("CLICKANDGO_WEB_DATA", "/tmp/clickandgo-web"))
TIEMPO_MAXIMO_SESION = 45 * 60

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static"))
app.config["JSON_AS_ASCII"] = False


# ----------------------------------------------------------------------
# Sesiones de consola (un proceso main.py por visitante)
# ----------------------------------------------------------------------
class SesionConsola:
    """Ejecuta ``main.py`` dentro de un pseudo-terminal aislado."""

    def __init__(self) -> None:
        self.id = uuid.uuid4().hex[:12]
        self.carpeta = Path(tempfile.mkdtemp(prefix=f"ckg-{self.id}-", dir=str(DIR_DATOS_WEB)))
        self.ruta_bd = self.carpeta / "sesion.db"
        self.creada = time.time()
        self.ultimo_acceso = time.time()
        self._buffer = ""
        self._lock = threading.Lock()

        self.master, esclavo = pty.openpty()
        flags = fcntl.fcntl(self.master, fcntl.F_GETFL)
        fcntl.fcntl(self.master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        entorno = {
            **os.environ,
            "CLICKANDGO_DB": str(self.ruta_bd),
            "PYTHONUNBUFFERED": "1",
            "PYTHONIOENCODING": "utf-8",
            "TERM": "xterm-256color",
            "COLUMNS": "100",
            "LINES": "40",
            "HOME": str(self.carpeta),
        }
        self.proceso = subprocess.Popen(
            [sys.executable, "-u", "main.py"],
            cwd=str(RAIZ),
            stdin=esclavo,
            stdout=esclavo,
            stderr=esclavo,
            env=entorno,
            preexec_fn=os.setsid,
            close_fds=True,
        )
        os.close(esclavo)
        self.inicial = self._esperar_salida_inicial()

    def _esperar_salida_inicial(self, segundos: float = 4.0) -> str:
        """Espera el banner del programa recien lanzado."""
        limite = time.time() + segundos
        texto = ""
        while time.time() < limite:
            texto += self.leer()
            if texto:
                break
            time.sleep(0.1)
        return texto

    # ------------------------------------------------------------------
    def leer(self) -> str:
        with self._lock:
            while True:
                try:
                    disponible, _, _ = select.select([self.master], [], [], 0.05)
                    if not disponible:
                        break
                    datos = os.read(self.master, 65536)
                    if not datos:
                        break
                    self._buffer += datos.decode("utf-8", errors="replace")
                except (OSError, ValueError):
                    break
            salida, self._buffer = self._buffer, ""
        return salida

    def escribir(self, texto: str) -> None:
        self.ultimo_acceso = time.time()
        if self.proceso.poll() is not None:
            return
        try:
            os.write(self.master, texto.encode("utf-8", errors="replace"))
        except OSError:
            pass

    def activa(self) -> bool:
        return self.proceso.poll() is None

    def cerrar(self) -> None:
        try:
            if self.activa():
                os.killpg(os.getpgid(self.proceso.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            os.close(self.master)
        except OSError:
            pass
        shutil.rmtree(self.carpeta, ignore_errors=True)


SESIONES: dict[str, SesionConsola] = {}
_CANDADO = threading.Lock()


def crear_sesion() -> SesionConsola:
    DIR_DATOS_WEB.mkdir(parents=True, exist_ok=True)
    with _CANDADO:
        limpiar_sesiones()
        if len(SESIONES) >= 25:  # tope defensivo de concurrencia
            mas_antigua = min(SESIONES.values(), key=lambda s: s.ultimo_acceso)
            SESIONES.pop(mas_antigua.id, None)
            mas_antigua.cerrar()
        sesion = SesionConsola()
        SESIONES[sesion.id] = sesion
    return sesion


def limpiar_sesiones() -> None:
    ahora = time.time()
    for identificador, sesion in list(SESIONES.items()):
        if not sesion.activa() or ahora - sesion.ultimo_acceso > TIEMPO_MAXIMO_SESION:
            SESIONES.pop(identificador, None)
            sesion.cerrar()


def obtener_sesion(identificador: str) -> SesionConsola | None:
    sesion = SESIONES.get(identificador)
    if sesion is None or not sesion.activa():
        if sesion is not None:
            SESIONES.pop(identificador, None)
            sesion.cerrar()
        return None
    sesion.ultimo_acceso = time.time()
    return sesion


# ----------------------------------------------------------------------
# Rutas
# ----------------------------------------------------------------------
@app.route("/")
def inicio():
    return render_template("index.html", activo="inicio")


@app.route("/arquitectura")
def arquitectura():
    return render_template("arquitectura.html", activo="arquitectura")


@app.route("/codigo")
def codigo():
    return render_template("codigo.html", activo="codigo")


@app.route("/pruebas")
def pruebas():
    return render_template("pruebas.html", activo="pruebas")


@app.route("/demo")
def demo():
    return render_template("demo.html", activo="demo")


@app.route("/descargas")
def descargas():
    return render_template("descargas.html", activo="descargas")


@app.route("/salud")
def salud():
    return jsonify({"estado": "ok", "sesiones": len(SESIONES)})


@app.route("/recursos/<path:nombre>")
def recursos(nombre: str):
    return send_from_directory(DIR_DOCS, nombre)


@app.route("/api/consola", methods=["POST"])
def api_crear():
    sesion = crear_sesion()
    return jsonify({"id": sesion.id, "salida": sesion.inicial + sesion.leer()})


@app.route("/api/consola/<identificador>", methods=["GET"])
def api_leer(identificador: str):
    sesion = obtener_sesion(identificador)
    if sesion is None:
        return jsonify({"activa": False, "salida": "\r\n[sesion finalizada]"}), 200
    return jsonify({"activa": sesion.activa(), "salida": sesion.leer()})


@app.route("/api/consola/<identificador>/entrada", methods=["POST"])
def api_entrada(identificador: str):
    sesion = obtener_sesion(identificador)
    if sesion is None:
        return jsonify({"ok": False, "mensaje": "sesion terminada"}), 200
    datos = request.get_json(silent=True) or {}
    texto = str(datos.get("texto", ""))
    sesion.escribir(texto + "\r")
    time.sleep(0.15)
    return jsonify({"ok": True, "salida": sesion.leer()})


@app.route("/api/consola/<identificador>", methods=["DELETE"])
def api_cerrar(identificador: str):
    sesion = SESIONES.pop(identificador, None)
    if sesion is not None:
        sesion.cerrar()
    return jsonify({"ok": True})


if __name__ == "__main__":
    DIR_DATOS_WEB.mkdir(parents=True, exist_ok=True)
    app.run(host="127.0.0.1", port=int(os.environ.get("PUERTO", "3030")), debug=False)
