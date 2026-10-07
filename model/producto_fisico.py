"""Producto tangible: se despacha por transporte y genera flete."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.producto import Producto


class ProductoFisico(Producto):
    """Bien tangible que requiere despacho terrestre con costo de flete."""

    TIPO = "FISICO"

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio_base_clp: float,
        stock: int,
        peso_kg: float,
        volumen_m3: float,
        tarifa_flete_base: float = 4500.0,
    ) -> None:
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._peso_kg = 0.0
        self._volumen_m3 = 0.0
        self._tarifa_flete_base = 0.0
        self.peso_kg = peso_kg
        self.volumen_m3 = volumen_m3
        self.tarifa_flete_base = tarifa_flete_base

    @property
    def peso_kg(self) -> float:
        return self._peso_kg

    @peso_kg.setter
    def peso_kg(self, valor: float) -> None:
        valor = float(valor)
        if valor <= 0:
            raise DatoInvalidoError("El peso debe ser mayor que cero.")
        self._peso_kg = round(valor, 3)

    @property
    def volumen_m3(self) -> float:
        return self._volumen_m3

    @volumen_m3.setter
    def volumen_m3(self, valor: float) -> None:
        valor = float(valor)
        if valor <= 0:
            raise DatoInvalidoError("El volumen debe ser mayor que cero.")
        self._volumen_m3 = round(valor, 4)

    @property
    def tarifa_flete_base(self) -> float:
        return self._tarifa_flete_base

    @tarifa_flete_base.setter
    def tarifa_flete_base(self, valor: float) -> None:
        valor = float(valor)
        if valor < 0:
            raise DatoInvalidoError("La tarifa base de flete no puede ser negativa.")
        self._tarifa_flete_base = round(valor, 2)

    def calcular_flete(self, distancia_km: float = 15.0) -> float:
        """Flete = tarifa base + peso + volumen + distancia recorrida."""
        variable = (self._peso_kg * 150) + (self._volumen_m3 * 800) + (distancia_km * 50)
        return round(self._tarifa_flete_base + variable, 2)

    def procesar_entrega(self, detalle) -> dict:
        flete = self.calcular_flete()
        return {
            "tipo": "DESPACHO_COURIER",
            "producto": self.nombre,
            "cantidad": detalle.cantidad,
            "flete_calculado": flete,
            "hereda_de": "ProductoFisico",
            "mensaje": (
                f"Se despacha por transporte. Peso {self._peso_kg} kg, "
                f"volumen {self._volumen_m3} m3. Flete calculado: ${flete:,.0f} CLP."
            ),
        }

    def calcular_precio_final(self, valor_dolar: float | None = None) -> float:
        return self._precio_base_clp

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update(
            {
                "peso_kg": self._peso_kg,
                "volumen_m3": self._volumen_m3,
                "tarifa_flete_base": self._tarifa_flete_base,
            }
        )
        return datos
