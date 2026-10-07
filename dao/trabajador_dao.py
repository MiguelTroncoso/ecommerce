"""Persistencia y autenticacion de los trabajadores (RBAC)."""

from __future__ import annotations

from dao.conexion import ConexionBD
from model.administrador import Administrador
from model.encargado_bodega import EncargadoBodega
from model.excepciones import AutenticacionError, RegistroNoEncontradoError
from model.trabajador import Trabajador


class TrabajadorDAO:
    """CRUD de trabajadores y verificacion de credenciales."""

    def __init__(self, conexion: ConexionBD) -> None:
        self._bd = conexion

    def crear(self, trabajador: Trabajador) -> Trabajador:
        self._bd.ejecutar(
            """
            INSERT INTO trabajadores (id_trabajador, nombre, correo, rol, extra,
                                      password_hash, salt)
            VALUES (:id_trabajador, :nombre, :correo, :rol, :extra,
                    :password_hash, :salt)
            """,
            trabajador.to_dict(),
        )
        return trabajador

    def listar(self) -> list[Trabajador]:
        filas = self._bd.consultar(
            "SELECT * FROM trabajadores ORDER BY rol, nombre COLLATE NOCASE"
        )
        return [self._fila_a_trabajador(fila) for fila in filas]

    def obtener(self, id_trabajador: str) -> Trabajador:
        fila = self._bd.consultar_uno(
            "SELECT * FROM trabajadores WHERE id_trabajador = :id", {"id": id_trabajador}
        )
        if fila is None:
            raise RegistroNoEncontradoError(f"No existe el trabajador '{id_trabajador}'.")
        return self._fila_a_trabajador(fila)

    def autenticar(self, nombre_usuario: str, password: str) -> Trabajador:
        fila = self._bd.consultar_uno(
            """
            SELECT * FROM trabajadores
             WHERE lower(nombre) = lower(:usuario) OR lower(correo) = lower(:usuario)
            """,
            {"usuario": str(nombre_usuario).strip()},
        )
        if fila is None:
            raise AutenticacionError("Usuario no encontrado.")
        trabajador = self._fila_a_trabajador(fila)
        if not trabajador.verificar_password(password):
            raise AutenticacionError("Contrasena incorrecta.")
        return trabajador

    def actualizar_password(self, trabajador: Trabajador, nueva_password: str) -> None:
        trabajador.definir_password(nueva_password)
        self._bd.ejecutar(
            """
            UPDATE trabajadores
               SET password_hash = :password_hash, salt = :salt
             WHERE id_trabajador = :id_trabajador
            """,
            {
                "password_hash": trabajador.password_hash,
                "salt": trabajador.salt,
                "id_trabajador": trabajador.id_trabajador,
            },
        )

    def contar(self) -> int:
        fila = self._bd.consultar_uno("SELECT COUNT(*) AS total FROM trabajadores")
        return int(fila["total"]) if fila else 0

    # ------------------------------------------------------------------
    @staticmethod
    def _fila_a_trabajador(fila) -> Trabajador:
        if fila["rol"] == "ADMINISTRADOR":
            return Administrador(
                fila["id_trabajador"],
                fila["nombre"],
                fila["correo"],
                int(fila["extra"] or 1),
                fila["password_hash"],
                fila["salt"],
            )
        return EncargadoBodega(
            fila["id_trabajador"],
            fila["nombre"],
            fila["correo"],
            fila["extra"] or "Zona A",
            fila["password_hash"],
            fila["salt"],
        )
