"""CRUD de productos con reconstruccion polimorfica desde la base de datos."""

from __future__ import annotations

from datetime import datetime

from dao.conexion import ConexionBD
from model.excepciones import RegistroNoEncontradoError
from model.producto import Producto
from model.producto_digital import ProductoDigital
from model.producto_electronica import ProductoElectronica
from model.producto_fisico import ProductoFisico
from model.producto_servicio import ProductoServicio

COLUMNAS = (
    "id_producto, tipo, nombre, precio_base_clp, precio_usd, stock, peso_kg, volumen_m3, "
    "tarifa_flete_base, enlace_descarga, licencia_activacion, peso_archivo_mb, "
    "fecha_agendada, direccion_visita, duracion_estimada_horas, garantia_meses"
)


class ProductoDAO:
    """Persistencia del catalogo (incluye los cuatro subtipos)."""

    def __init__(self, conexion: ConexionBD) -> None:
        self._bd = conexion

    # ------------------------------------------------------------------
    def crear(self, producto: Producto) -> Producto:
        datos = producto.to_dict()
        self._bd.ejecutar(
            f"""
            INSERT INTO productos ({COLUMNAS})
            VALUES (:id_producto, :tipo, :nombre, :precio_base_clp, :precio_usd, :stock,
                    :peso_kg, :volumen_m3, :tarifa_flete_base, :enlace_descarga,
                    :licencia_activacion, :peso_archivo_mb, :fecha_agendada,
                    :direccion_visita, :duracion_estimada_horas, :garantia_meses)
            """,
            datos,
        )
        return producto

    def listar(self, tipo: str | None = None) -> list[Producto]:
        if tipo:
            filas = self._bd.consultar(
                f"SELECT {COLUMNAS} FROM productos WHERE tipo = :tipo ORDER BY nombre COLLATE NOCASE",
                {"tipo": tipo.upper()},
            )
        else:
            filas = self._bd.consultar(
                f"SELECT {COLUMNAS} FROM productos ORDER BY tipo, nombre COLLATE NOCASE"
            )
        return [self.fila_a_producto(fila) for fila in filas]

    def obtener(self, id_producto: str) -> Producto:
        fila = self._bd.consultar_uno(
            f"SELECT {COLUMNAS} FROM productos WHERE id_producto = :id",
            {"id": id_producto},
        )
        if fila is None:
            raise RegistroNoEncontradoError(f"No existe el producto '{id_producto}'.")
        return self.fila_a_producto(fila)

    def actualizar(self, producto: Producto) -> None:
        datos = producto.to_dict()
        datos["id_producto"] = producto.id_producto
        self._bd.ejecutar(
            """
            UPDATE productos
               SET nombre = :nombre,
                   precio_base_clp = :precio_base_clp,
                   precio_usd = :precio_usd,
                   stock = :stock,
                   peso_kg = :peso_kg,
                   volumen_m3 = :volumen_m3,
                   tarifa_flete_base = :tarifa_flete_base,
                   enlace_descarga = :enlace_descarga,
                   licencia_activacion = :licencia_activacion,
                   peso_archivo_mb = :peso_archivo_mb,
                   fecha_agendada = :fecha_agendada,
                   direccion_visita = :direccion_visita,
                   duracion_estimada_horas = :duracion_estimada_horas,
                   garantia_meses = :garantia_meses
             WHERE id_producto = :id_producto
            """,
            datos,
        )

    def actualizar_stock(self, id_producto: str, nuevo_stock: int) -> None:
        self._bd.ejecutar(
            "UPDATE productos SET stock = :stock WHERE id_producto = :id",
            {"stock": int(nuevo_stock), "id": id_producto},
        )

    def eliminar(self, id_producto: str) -> bool:
        with self._bd.conectar() as conexion:
            cursor = conexion.execute(
                "DELETE FROM productos WHERE id_producto = :id", {"id": id_producto}
            )
            conexion.commit()
            return cursor.rowcount > 0

    def contar(self) -> int:
        fila = self._bd.consultar_uno("SELECT COUNT(*) AS total FROM productos")
        return int(fila["total"]) if fila else 0

    # ------------------------------------------------------------------
    @staticmethod
    def fila_a_producto(fila) -> Producto:
        tipo = fila["tipo"]
        if tipo == "ELECTRONICA":
            return ProductoElectronica(
                fila["id_producto"],
                fila["nombre"],
                fila["precio_usd"],
                fila["stock"],
                fila["peso_kg"],
                fila["volumen_m3"],
                fila["garantia_meses"] or 12,
                fila["tarifa_flete_base"] or 4500.0,
            )
        if tipo == "FISICO":
            return ProductoFisico(
                fila["id_producto"],
                fila["nombre"],
                fila["precio_base_clp"],
                fila["stock"],
                fila["peso_kg"],
                fila["volumen_m3"],
                fila["tarifa_flete_base"] or 4500.0,
            )
        if tipo == "DIGITAL":
            return ProductoDigital(
                fila["id_producto"],
                fila["nombre"],
                fila["precio_base_clp"],
                fila["stock"],
                fila["enlace_descarga"],
                fila["licencia_activacion"],
                fila["peso_archivo_mb"],
            )
        if tipo == "SERVICIO":
            return ProductoServicio(
                fila["id_producto"],
                fila["nombre"],
                fila["precio_base_clp"],
                fila["stock"],
                datetime.strptime(fila["fecha_agendada"], "%Y-%m-%d %H:%M"),
                fila["direccion_visita"],
                fila["duracion_estimada_horas"] or 1,
            )
        raise RegistroNoEncontradoError(f"Tipo de producto desconocido: {tipo}")
