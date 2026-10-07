"""Excepciones propias del sistema ClickAndGo.

Cada regla de negocio que impide una operacion se representa con una
excepcion dedicada. Esto permite capturarlas de forma especifica (nunca con
un ``except`` generico) y entregar un mensaje claro al operador sin detener
la ejecucion del programa.
"""


class ClickAndGoError(Exception):
    """Excepcion base del dominio ClickAndGo."""


class DatoInvalidoError(ClickAndGoError):
    """La entrada recibida no cumple el tipo, formato o rango esperado."""


class IdentificadorInvalidoError(DatoInvalidoError):
    """El RUT o correo del cliente no supera la validacion obligatoria."""


class StockInsuficienteError(ClickAndGoError):
    """Regla de negocio 1: no se puede confirmar un pedido sin stock."""

    def __init__(self, producto: str, solicitado: int, disponible: int) -> None:
        self.producto = producto
        self.solicitado = solicitado
        self.disponible = disponible
        super().__init__(
            f"Stock insuficiente para '{producto}': se solicitan {solicitado} "
            f"unidades y solo hay {disponible} disponibles."
        )


class PedidoNoPagadoError(ClickAndGoError):
    """Regla de negocio 2: no se puede despachar un pedido sin pago."""

    def __init__(self, id_pedido: str, estado_pago: str) -> None:
        self.id_pedido = id_pedido
        self.estado_pago = estado_pago
        super().__init__(
            f"El pedido {id_pedido} no puede despacharse: su estado de pago "
            f"es '{estado_pago}' y se exige 'PAGADO'."
        )


class SinPermisoError(ClickAndGoError):
    """El trabajador autenticado no tiene el permiso requerido (RBAC)."""

    def __init__(self, accion: str, rol: str) -> None:
        self.accion = accion
        self.rol = rol
        super().__init__(
            f"El rol '{rol}' no tiene autorizacion para {accion}."
        )


class AutenticacionError(ClickAndGoError):
    """Las credenciales entregadas no corresponden a un trabajador valido."""


class IndicadorNoDisponibleError(ClickAndGoError):
    """No fue posible obtener el indicador externo (por ejemplo el dolar)."""


class RegistroNoEncontradoError(ClickAndGoError):
    """El registro solicitado no existe en la base de datos."""


class PedidoVacioError(ClickAndGoError):
    """Un pedido sin lineas de detalle no es una transaccion valida."""
