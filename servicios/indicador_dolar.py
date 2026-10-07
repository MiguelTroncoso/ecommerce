"""Consumo del indicador externo (dolar observado) publicado por mindicador.cl.

Cumple los criterios 3.1.1 y 3.1.3: usa la libreria oficial ``requests``,
define un tiempo maximo de espera y ante cualquier falla informa el problema
manteniendo la continuidad del sistema.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import requests

from model.excepciones import IndicadorNoDisponibleError

URL_DOLAR = "https://mindicador.cl/api/dolar"
TIEMPO_MAXIMO_ESPERA = 5.0


class ValorDolar:
    """Valor del dolar junto con su fecha y su origen."""

    def __init__(self, valor: float, fecha: str, fuente: str) -> None:
        self.valor = float(valor)
        self.fecha = fecha
        self.fuente = fuente

    def __str__(self) -> str:
        return f"${self.valor:,.2f} CLP/USD ({self.fecha}) - fuente: {self.fuente}"


class ServicioIndicadorDolar:
    """Cliente del indicador externo con respaldo local."""

    def __init__(
        self,
        url: str = URL_DOLAR,
        timeout: float = TIEMPO_MAXIMO_ESPERA,
        ruta_respaldo: str | os.PathLike | None = None,
    ) -> None:
        self._url = url
        self._timeout = timeout
        self._ruta_respaldo = Path(
            ruta_respaldo or Path(__file__).resolve().parent.parent / "datos" / "dolar_respaldo.json"
        )

    # ------------------------------------------------------------------
    def obtener_valor_dolar(self) -> ValorDolar:
        """Consulta mindicador.cl. Lanza IndicadorNoDisponibleError si falla."""
        try:
            respuesta = requests.get(
                self._url,
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
                f"No fue posible obtener el dolar desde {self._url}: {error}"
            ) from error

        indicador = ValorDolar(valor, fecha, "mindicador.cl (API en linea)")
        self._guardar_respaldo(indicador)
        return indicador

    # ------------------------------------------------------------------
    def ultimo_valor_conocido(self) -> ValorDolar | None:
        try:
            datos = json.loads(self._ruta_respaldo.read_text(encoding="utf-8"))
            return ValorDolar(
                datos["valor"], datos["fecha"], "respaldo local (ultimo valor conocido)"
            )
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _guardar_respaldo(self, indicador: ValorDolar) -> None:
        try:
            self._ruta_respaldo.parent.mkdir(parents=True, exist_ok=True)
            self._ruta_respaldo.write_text(
                json.dumps(
                    {"valor": indicador.valor, "fecha": indicador.fecha},
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

        - Si la API responde, entrega el valor del dia y sin advertencia.
        - Si la API falla, entrega el ultimo valor conocido y una advertencia.
        - Si no hay conexion ni respaldo, entrega ``(None, advertencia)``.
        """
        try:
            return self.obtener_valor_dolar(), None
        except IndicadorNoDisponibleError as error:
            respaldo = self.ultimo_valor_conocido()
            if respaldo is not None:
                return respaldo, (
                    f"{error} Se usara el ultimo valor conocido "
                    f"(${respaldo.valor:,.2f} del {respaldo.fecha})."
                )
            return None, f"{error} No hay un valor de respaldo disponible."
