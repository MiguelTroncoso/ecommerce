"""Persistencia de la transaccion y sus lineas de detalle."""

from __future__ import annotations

from datetime import datetime

from dao.cliente_dao import ClienteDAO
from dao.conexion import ConexionBD
from dao.producto_dao import ProductoDAO
from model.detalle_pedido import DetallePedido
from model.excepciones import RegistroNoEncontradoError
from model.pedido import Pedido


class PedidoDAO:
    """Guarda el pedido y sus lineas dentro de una sola transaccion SQL."""

    def __init__(self, conexion: ConexionBD) -> None:
        self._bd = conexion
        self._clientes = ClienteDAO(conexion)
        self._productos = ProductoDAO(conexion)

    # ------------------------------------------------------------------
    def crear(self, pedido: Pedido) -> Pedido:
        """Inserta cabecera y detalles en una unica transaccion (atomica)."""
        with self._bd.conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO pedidos (id_pedido, id_cliente, fecha_creacion, estado_pago,
                                     estado_entrega, total_flete_clp, total_final_clp)
                VALUES (:id_pedido, :id_cliente, :fecha_creacion, :estado_pago,
                        :estado_entrega, :total_flete_clp, :total_final_clp)
                """,
                pedido.to_dict(),
            )
            for detalle in pedido.detalles:
                conexion.execute(
                    """
                    INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad,
                                                precio_unitario_congelado)
                    VALUES (:id_pedido, :id_producto, :cantidad, :precio)
                    """,
                    {
                        "id_pedido": pedido.id_pedido,
                        "id_producto": detalle.producto.id_producto,
                        "cantidad": detalle.cantidad,
                        "precio": detalle.precio_unitario_congelado,
                    },
                )
            conexion.commit()
        return pedido

    def listar(self, id_cliente: str | None = None) -> list[Pedido]:
        if id_cliente:
            filas = self._bd.consultar(
                "SELECT * FROM pedidos WHERE id_cliente = :id ORDER BY fecha_creacion DESC",
                {"id": id_cliente},
            )
        else:
            filas = self._bd.consultar(
                "SELECT * FROM pedidos ORDER BY fecha_creacion DESC"
            )
        return [self._fila_a_pedido(fila) for fila in filas]

    def obtener(self, id_pedido: str) -> Pedido:
        fila = self._bd.consultar_uno(
            "SELECT * FROM pedidos WHERE id_pedido = :id", {"id": id_pedido}
        )
        if fila is None:
            raise RegistroNoEncontradoError(f"No existe el pedido '{id_pedido}'.")
        return self._fila_a_pedido(fila)

    def actualizar_estado(
        self, id_pedido: str, estado_pago: str, estado_entrega: str, total_final_clp: float
    ) -> None:
        self._bd.ejecutar(
            """
            UPDATE pedidos
               SET estado_pago = :pago,
                   estado_entrega = :entrega,
                   total_final_clp = :total
             WHERE id_pedido = :id
            """,
            {
                "pago": estado_pago,
                "entrega": estado_entrega,
                "total": round(float(total_final_clp), 2),
                "id": id_pedido,
            },
        )

    def eliminar(self, id_pedido: str) -> bool:
        with self._bd.conectar() as conexion:
            cursor = conexion.execute(
                "DELETE FROM pedidos WHERE id_pedido = :id", {"id": id_pedido}
            )
            conexion.commit()
            return cursor.rowcount > 0

    def contar(self) -> int:
        fila = self._bd.consultar_uno("SELECT COUNT(*) AS total FROM pedidos")
        return int(fila["total"]) if fila else 0

    # ------------------------------------------------------------------
    def _fila_a_pedido(self, fila) -> Pedido:
        cliente = self._clientes.obtener(fila["id_cliente"])
        pedido = Pedido(
            fila["id_pedido"],
            cliente,
            datetime.strptime(fila["fecha_creacion"], "%Y-%m-%d %H:%M:%S"),
            fila["estado_pago"],
            fila["estado_entrega"],
        )
        for detalle_fila in self._bd.consultar(
            "SELECT * FROM detalle_pedido WHERE id_pedido = :id ORDER BY id_detalle",
            {"id": fila["id_pedido"]},
        ):
            producto = self._productos.obtener(detalle_fila["id_producto"])
            pedido._detalles.append(  # noqa: SLF001 - reconstruccion controlada
                DetallePedido(
                    producto,
                    detalle_fila["cantidad"],
                    detalle_fila["precio_unitario_congelado"],
                    detalle_fila["id_detalle"],
                )
            )
        pedido.calcular_total()
        return pedido
