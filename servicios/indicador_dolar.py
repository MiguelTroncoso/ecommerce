"""Consumo del indicador externo (dolar observado) con proveedores de respaldo.

El servicio consulta una cadena de proveedores publicos con el mismo formato
de respuesta. Si el primero no responde, intenta con el siguiente y, como
ultima instancia, usa el ultimo valor guardado en el disco.

Orden de intentos:

1. ``https://mindicador.cl/api/`` (proveedor principal)
2. ``https://findic.cl/api/``    (proveedor de respaldo)
3. ``datos/dolar_respaldo.json`` (ultimo valor conocido)

Cumple los criterios 3.1.1 y 3.1.3: usa la libreria oficial ``requests``,
define un tiempo maximo de espera por intento y ante cualquier falla informa
el problema manteniendo la continuidad del sistema.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import requests

from model.excepciones import IndicadorNoDisponibleError

PROVEEDORES = (
    ("mindicador.cl", "https://mindicador.cl/api/"),
    ("findic.cl", "https://findic.cl/api/"),
)
RECURSO_DOLAR = "dolar"
TIEMPO_MAXIMO_ESPERA = 5.0


class ValorDolar:
    """Valor del dolar junto con su fecha y su origen."""

    def __init__(self, valor: float, fecha: str, fuente: str, proveedor: str = "") -> None:
        self.valor = float(valor)
        self.fecha = fecha
        self.fuente = fuente
        self.proveedor = proveedor or fuente

    def __str__(self) -> str:
        return f"${self.valor:,.2f} CLP/USD ({self.fecha}) - fuente: {self.fuente}"


class ServicioIndicadorDolar:
    """Cliente del indicador externo con varios proveedores y respaldo local."""

    def __init__(
        self,
        proveedores: list[tuple[str, str]] | None = None,
        timeout: float = TIEMPO_MAXIMO_ESPERA,
        ruta_respaldo: str | os.PathLike | None = None,
        url: str | None = None,
    ) -> None:
        if url:
            # Compatibilidad: un unico proveedor indicado a mano.
            self._proveedores = [("personalizado", url)]
        else:
            self._proveedores = list(proveedores or PROVEEDORES)
        self._timeout = timeout
        self._ruta_respaldo = Path(
            ruta_respaldo or Path(__file__).resolve().parent.parent / "datos" / "dolar_respaldo.json"
        )
        # Errores de los proveedores que fallaron antes de obtener el valor.
        self.ultimos_errores: list[str] = []

    # ------------------------------------------------------------------
    def obtener_valor_dolar(self) -> ValorDolar:
        """Recorre los proveedores en orden hasta obtener un valor.

        Lanza IndicadorNoDisponibleError solo si fallan todos.
        """
        self.ultimos_errores = []
        for nombre, base in self._proveedores:
            try:
                return self._consultar_proveedor(nombre, base)
            except IndicadorNoDisponibleError as error:
                self.ultimos_errores.append(f"{nombre}: {error}")
        raise IndicadorNoDisponibleError(
            "Ningun proveedor de indicadores respondio. " + " | ".join(self.ultimos_errores)
        )

    def _consultar_proveedor(self, nombre: str, base: str) -> ValorDolar:
        url = f"{base.rstrip('/')}/{RECURSO_DOLAR}"
        try:
            respuesta = requests.get(
                url,
                timeout=self._timeout,
                headers={"User-Agent": "ClickAndGo/2.0 (INACAP TI3V21)"},
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
            serie = datos.get("serie") or []
            if not serie:
                raise ValueError("La respuesta no contiene la serie del dolar.")
            ultimo = serie[0]
            valor = float(ultimo["valor"])
            fecha = str(ultimo.get("fecha", datetime.now().isoformat()))[:10]
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            raise IndicadorNoDisponibleError(
                f"No fue posible obtener el dolar desde {url}: {error}"
            ) from error

        indicador = ValorDolar(valor, fecha, f"{nombre} (API en linea)", nombre)
        self._guardar_respaldo(indicador)
        return indicador

    # ------------------------------------------------------------------
    def ultimo_valor_conocido(self) -> ValorDolar | None:
        try:
            datos = json.loads(self._ruta_respaldo.read_text(encoding="utf-8"))
            return ValorDolar(
                datos["valor"],
                datos["fecha"],
                "respaldo local (ultimo valor conocido)",
                datos.get("proveedor", "respaldo local"),
            )
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _guardar_respaldo(self, indicador: ValorDolar) -> None:
        try:
            self._ruta_respaldo.parent.mkdir(parents=True, exist_ok=True)
            self._ruta_respaldo.write_text(
                json.dumps(
                    {
                        "valor": indicador.valor,
                        "fecha": indicador.fecha,
                        "proveedor": indicador.proveedor,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError:
            # El respaldo es una comodidad: si no se puede escribir, el
            # programa continua funcionando sin el.
            pass

    # ------------------------------------------------------------------
    def valor_para_calculo(self) -> tuple[ValorDolar | None, str | None]:
        """Devuelve ``(indicador, advertencia)`` sin lanzar excepciones.

        - Si responde el proveedor principal, entrega el valor del dia sin advertencia.
        - Si responde un proveedor de respaldo, avisa cual se uso.
        - Si fallan todos, entrega el ultimo valor conocido y una advertencia.
        - Si no hay conexion ni respaldo, entrega ``(None, advertencia)``.
        """
        try:
            indicador = self.obtener_valor_dolar()
            if self.ultimos_errores:
                aviso = (
                    f"El proveedor principal no respondio ({self.ultimos_errores[0]}). "
                    f"Se uso el respaldo {indicador.proveedor}."
                )
                return indicador, aviso
            return indicador, None
        except IndicadorNoDisponibleError as error:
            respaldo = self.ultimo_valor_conocido()
            if respaldo is not None:
                return respaldo, (
                    f"{error} Se usara el ultimo valor conocido "
                    f"(${respaldo.valor:,.2f} del {respaldo.fecha})."
                )
            return None, f"{error} No hay un valor de respaldo disponible."
