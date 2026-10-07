"""Electronica importada: precio en USD convertido con el dolar del dia."""

from __future__ import annotations

from model.excepciones import DatoInvalidoError
from model.producto_fisico import ProductoFisico


class ProductoElectronica(ProductoFisico):
    """Producto fisico importado, cotizado en dolares.

    Es el requisito de "precio dependiente de un indicador externo": hereda
    de :class:`ProductoFisico` y sobrescribe ``calcular_precio_final()``
    multiplicando su costo en USD por el valor del dolar observado.
    """

    TIPO = "ELECTRONICA"

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio_usd: float,
        stock: int,
        peso_kg: float,
        volumen_m3: float,
        garantia_meses: int = 12,
        tarifa_flete_base: float = 4500.0,
    ) -> None:
        super().__init__(
            id_producto,
            nombre,
            precio_base_clp=0.0,
            stock=stock,
            peso_kg=peso_kg,
            volumen_m3=volumen_m3,
            tarifa_flete_base=tarifa_flete_base,
        )
        self._precio_usd = 0.0
        self._garantia_meses = 0
        self.precio_usd = precio_usd
        self.garantia_meses = garantia_meses

    @property
    def precio_usd(self) -> float:
        return self._precio_usd

    @precio_usd.setter
    def precio_usd(self, valor: float) -> None:
        valor = float(valor)
        if valor <= 0:
            raise DatoInvalidoError("El precio en USD debe ser mayor que cero.")
        self._precio_usd = round(valor, 2)

    @property
    def garantia_meses(self) -> int:
        return self._garantia_meses

    @garantia_meses.setter
    def garantia_meses(self, valor: int) -> None:
        valor = int(valor)
        if valor < 0 or valor > 120:
            raise DatoInvalidoError("La garantia debe estar entre 0 y 120 meses.")
        self._garantia_meses = valor

    def calcular_precio_final(self, valor_dolar: float | None = None) -> float:
        """Convierte el costo en USD a CLP usando el indicador entregado."""
        if valor_dolar is None or float(valor_dolar) <= 0:
            raise DatoInvalidoError(
                "Para cotizar electronica importada se requiere el valor del dolar del dia."
            )
        return round(self._precio_usd * float(valor_dolar), 2)

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update(
            {
                "precio_usd": self._precio_usd,
                "garantia_meses": self._garantia_meses,
                "precio_base_clp": self._precio_base_clp,
            }
        )
        return datos

    def __str__(self) -> str:
        return (
            f"{self.descripcion_corta} - USD {self._precio_usd:,.2f} "
            f"(garantia {self._garantia_meses} meses) - stock {self._stock}"
        )
