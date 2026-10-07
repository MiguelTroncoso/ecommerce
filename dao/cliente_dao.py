"""CRUD de clientes con consultas parametrizadas."""

from __future__ import annotations

from dao.conexion import ConexionBD
from model.cliente import Cliente
from model.excepciones import RegistroNoEncontradoError


class ClienteDAO:
    """Operaciones de creacion, lectura, actualizacion y borrado."""

    def __init__(self, conexion: ConexionBD) -> None:
        self._bd = conexion

    def crear(self, cliente: Cliente) -> Cliente:
        self._bd.ejecutar(
            """
            INSERT INTO clientes (id_cliente, nombre, identificador, tipo_identificador)
            VALUES (:id_cliente, :nombre, :identificador, :tipo_identificador)
            """,
            cliente.to_dict(),
        )
        return cliente

    def listar(self) -> list[Cliente]:
        filas = self._bd.consultar(
            "SELECT * FROM clientes ORDER BY nombre COLLATE NOCASE"
        )
        return [Cliente.from_row(fila) for fila in filas]

    def obtener(self, id_cliente: str) -> Cliente:
        fila = self._bd.consultar_uno(
            "SELECT * FROM clientes WHERE id_cliente = :id", {"id": id_cliente}
        )
        if fila is None:
            raise RegistroNoEncontradoError(f"No existe el cliente '{id_cliente}'.")
        return Cliente.from_row(fila)

    def buscar_por_identificador(self, identificador: str) -> Cliente | None:
        fila = self._bd.consultar_uno(
            "SELECT * FROM clientes WHERE identificador = :identificador",
            {"identificador": identificador},
        )
        return Cliente.from_row(fila) if fila else None

    def actualizar(self, cliente: Cliente) -> None:
        self._bd.ejecutar(
            """
            UPDATE clientes
               SET nombre = :nombre,
                   identificador = :identificador,
                   tipo_identificador = :tipo_identificador
             WHERE id_cliente = :id_cliente
            """,
            cliente.to_dict(),
        )

    def eliminar(self, id_cliente: str) -> bool:
        with self._bd.conectar() as conexion:
            cursor = conexion.execute(
                "DELETE FROM clientes WHERE id_cliente = :id", {"id": id_cliente}
            )
            conexion.commit()
            return cursor.rowcount > 0

    def contar(self) -> int:
        fila = self._bd.consultar_uno("SELECT COUNT(*) AS total FROM clientes")
        return int(fila["total"]) if fila else 0
