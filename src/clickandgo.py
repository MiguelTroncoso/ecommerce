"""
Plataforma E-Commerce ClickAndGo
Implementación del Modelo de Clases UML bajo estándar POO (INACAP TI3V21)
"""

from abc import ABC, abstractmethod
from datetime import datetime
import re

class Cliente:
    """Modela al comprador y centraliza la validación de RUT o Email."""
    def __init__(self, id_cliente: str, nombre: str, identificador: str, tipo_identificador: str = "RUT"):
        self._id_cliente = id_cliente
        self._nombre = nombre
        self._identificador = identificador.strip()
        self._tipo_identificador = tipo_identificador.upper()

    def validar_identificador(self) -> bool:
        """Valida algoritmo Módulo 11 (RUT chileno) o formato sintáctico de Email."""
        if self._tipo_identificador == "EMAIL":
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            return bool(re.match(pattern, self._identificador))
        
        # Validación RUT chileno (Módulo 11)
        rut_limpio = self._identificador.replace(".", "").replace("-", "").upper()
        if len(rut_limpio) < 2:
            return False
        
        cuerpo = rut_limpio[:-1]
        dv = rut_limpio[-1]

        if not cuerpo.isdigit():
            return False

        # Algoritmo Módulo 11
        suma = 0
        multiplo = 2
        for d in reversed(cuerpo):
            suma += int(d) * multiplo
            multiplo = 2 if multiplo == 7 else multiplo + 1

        resto = suma % 11
        dv_esperado = 11 - resto
        if dv_esperado == 11:
            dv_calculado = "0"
        elif dv_esperado == 10:
            dv_calculado = "K"
        else:
            dv_calculado = str(dv_esperado)

        return dv == dv_calculado

    def get_identificador(self) -> str:
        return self._identificador

    def get_nombre(self) -> str:
        return self._nombre


class DetallePedido:
    """Modela una línea comercial dentro de un pedido, congelando precio unitario."""
    def __init__(self, producto: "Producto", cantidad: int, precio_unitario: float):
        self._producto = producto
        self._cantidad = cantidad
        self._precio_unitario_congelado = precio_unitario

    def calcular_subtotal(self) -> float:
        return self._cantidad * self._precio_unitario_congelado

    def get_producto(self) -> "Producto":
        return self._producto

    def get_cantidad(self) -> int:
        return self._cantidad

    def get_precio_unitario(self) -> float:
        return self._precio_unitario_congelado


class Producto(ABC):
    """Clase base abstracta que define el contrato general de catálogo e inventario."""
    def __init__(self, id_producto: str, nombre: str, precio_base_clp: float, stock: int):
        self._id_producto = id_producto
        self._nombre = nombre
        self._precio_base_clp = precio_base_clp
        self._stock = stock

    @abstractmethod
    def procesar_entrega(self, detalle: DetallePedido) -> dict:
        """Polimorfismo: resuelve la entrega según la mecánica del producto."""
        pass

    @abstractmethod
    def calcular_precio_final(self, indicador_dolar: float = 950.0) -> float:
        """Polimorfismo: calcula precio según moneda o indicadores externos."""
        pass

    def descontar_stock(self, cantidad: int) -> bool:
        if self.tiene_stock_suficiente(cantidad):
            self._stock -= cantidad
            return True
        return False

    def tiene_stock_suficiente(self, cantidad: int) -> bool:
        return self._stock >= cantidad

    def get_stock(self) -> int:
        return self._stock

    def get_nombre(self) -> str:
        return self._nombre

    def get_precio_base(self) -> float:
        return self._precio_base_clp

    def set_precio_base(self, nuevo_precio: float):
        self._precio_base_clp = nuevo_precio


class ProductoFisico(Producto):
    """Bienes tangibles con cálculo de flete y despacho terrestre."""
    def __init__(self, id_producto: str, nombre: str, precio_base_clp: float, stock: int,
                 peso_kg: float, volumen_m3: float, tarifa_flete_base: float = 4500.0):
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._peso_kg = peso_kg
        self._volumen_m3 = volumen_m3
        self._tarifa_flete_base = tarifa_flete_base

    def calcular_flete(self, distancia_km: float = 15.0) -> float:
        flete_variable = (self._peso_kg * 150) + (self._volumen_m3 * 800) + (distancia_km * 50)
        return round(self._tarifa_flete_base + flete_variable, 2)

    def procesar_entrega(self, detalle: DetallePedido) -> dict:
        flete = self.calcular_flete()
        return {
            "tipo": "DESPACHO_COURIER",
            "producto": self._nombre,
            "cantidad": detalle.get_cantidad(),
            "flete_calculado": flete,
            "mensaje": f"Orden de transporte generada. Peso: {self._peso_kg}kg. Flete: ${flete:,.0f} CLP."
        }

    def calcular_precio_final(self, indicador_dolar: float = 950.0) -> float:
        return self._precio_base_clp


class ProductoElectronica(ProductoFisico):
    """Subclase de ProductoFisico para bienes cotizados en USD con tasa de cambio diaria."""
    def __init__(self, id_producto: str, nombre: str, precio_usd: float, stock: int,
                 peso_kg: float, volumen_m3: float, garantia_meses: int = 12):
        super().__init__(id_producto, nombre, 0.0, stock, peso_kg, volumen_m3)
        self._precio_usd = precio_usd
        self._garantia_meses = garantia_meses

    def calcular_precio_final(self, indicador_dolar: float = 950.0) -> float:
        """Cumplimiento Requisito 6: Precio dependiente de indicador externo (USD -> CLP)."""
        return round(self._precio_usd * indicador_dolar, 2)

    def get_precio_usd(self) -> float:
        return self._precio_usd


class ProductoDigital(Producto):
    """Bienes intangibles sin flete ($0) con emisión de enlaces o licencias."""
    def __init__(self, id_producto: str, nombre: str, precio_base_clp: float, stock: int,
                 enlace_descarga: str, licencia_activacion: str, peso_archivo_mb: float):
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._enlace_descarga = enlace_descarga
        self._licencia_activacion = licencia_activacion
        self._peso_archivo_mb = peso_archivo_mb

    def procesar_entrega(self, detalle: DetallePedido) -> dict:
        return {
            "tipo": "DESCARGA_DIGITAL",
            "producto": self._nombre,
            "cantidad": detalle.get_cantidad(),
            "flete_calculado": 0.0,
            "licencia": self.emitir_licencia(),
            "enlace": self._enlace_descarga,
            "mensaje": f"Entrega inmediata sin flete ($0). Licencia: {self._licencia_activacion}."
        }

    def calcular_precio_final(self, indicador_dolar: float = 950.0) -> float:
        return self._precio_base_clp

    def emitir_licencia(self) -> str:
        return self._licencia_activacion


class ProductoServicio(Producto):
    """Prestaciones técnicas presenciales con agenda de fecha y sin flete de carga."""
    def __init__(self, id_producto: str, nombre: str, precio_base_clp: float, stock: int,
                 fecha_agendada: datetime, direccion_visita: str, duracion_estimada_horas: int):
        super().__init__(id_producto, nombre, precio_base_clp, stock)
        self._fecha_agendada = fecha_agendada
        self._direccion_visita = direccion_visita
        self._duracion_estimada_horas = duracion_estimada_horas

    def procesar_entrega(self, detalle: DetallePedido) -> dict:
        return {
            "tipo": "SERVICIO_TECNICO",
            "producto": self._nombre,
            "cantidad": detalle.get_cantidad(),
            "flete_calculado": 0.0,
            "agenda": self._fecha_agendada.strftime("%Y-%m-%d %H:%M"),
            "direccion": self._direccion_visita,
            "mensaje": f"Técnico asignado para el {self._fecha_agendada.strftime('%d/%m/%Y a las %H:%M')} hrs."
        }

    def calcular_precio_final(self, indicador_dolar: float = 950.0) -> float:
        return self._precio_base_clp

    def agendar_fecha(self, fecha: datetime) -> bool:
        self._fecha_agendada = fecha
        return True


class Trabajador(ABC):
    """Clase base abstracta para RBAC (Role-Based Access Control)."""
    def __init__(self, id_trabajador: str, nombre: str, correo: str):
        self._id_trabajador = id_trabajador
        self._nombre = nombre
        self._correo = correo

    @abstractmethod
    def puede_modificar_catalogo(self) -> bool:
        pass

    @abstractmethod
    def puede_despachar(self) -> bool:
        pass

    def get_nombre(self) -> str:
        return self._nombre


class EncargadoBodega(Trabajador):
    """Personal de almacén: puede despachar pero NO modificar catálogo."""
    def __init__(self, id_trabajador: str, nombre: str, correo: str, zona_bodega: str = "Zona A"):
        super().__init__(id_trabajador, nombre, correo)
        self._zona_bodega_asignada = zona_bodega

    def puede_modificar_catalogo(self) -> bool:
        return False

    def puede_despachar(self) -> bool:
        return True

    def registrar_preparacion(self, pedido: "Pedido") -> str:
        return f"Pedido {pedido.get_id()} preparado por {self._nombre} en {self._zona_bodega_asignada}."


class Administrador(Trabajador):
    """Personal gerencial con permisos totales de catálogo y despacho."""
    def __init__(self, id_trabajador: str, nombre: str, correo: str, nivel_acceso: int = 1):
        super().__init__(id_trabajador, nombre, correo)
        self._nivel_acceso = nivel_acceso

    def puede_modificar_catalogo(self) -> bool:
        return True

    def puede_despachar(self) -> bool:
        return True

    def actualizar_precio(self, producto: Producto, nuevo_precio: float):
        producto.set_precio_base(nuevo_precio)

    def registrar_nuevo_producto(self, producto: Producto) -> str:
        return f"Producto {producto.get_nombre()} registrado por Admin {self._nombre}."


class Pedido:
    """Transacción comercial compuesta de detalles multi-línea."""
    def __init__(self, id_pedido: str, cliente: Cliente):
        self._id_pedido = id_pedido
        self._cliente = cliente
        self._fecha_creacion = datetime.now()
        self._estado_pago = "PENDIENTE"       # PENDIENTE | PAGADO | RECHAZADO
        self._estado_entrega = "PENDIENTE"    # PENDIENTE | DESPACHADO | ENTREGADO
        self._total_flete_clp = 0.0
        self._total_final_clp = 0.0
        self._detalles: list[DetallePedido] = []

    def get_id(self) -> str:
        return self._id_pedido

    def get_estado_pago(self) -> str:
        return self._estado_pago

    def get_estado_entrega(self) -> str:
        return self._estado_entrega

    def agregar_linea(self, producto: Producto, cantidad: int, tasa_dolar: float = 950.0) -> bool:
        if cantidad <= 0:
            return False
        precio_congelado = producto.calcular_precio_final(tasa_dolar)
        detalle = DetallePedido(producto, cantidad, precio_congelado)
        self._detalles.append(detalle)
        return True

    def confirmar_pedido(self) -> bool:
        """Regla 1: Bloquea confirmación si el cliente es inválido o no hay stock."""
        if not self._cliente.validar_identificador():
            return False

        if not self._detalles:
            return False

        for detalle in self._detalles:
            if not detalle.get_producto().tiene_stock_suficiente(detalle.get_cantidad()):
                return False  # Bloqueo por falta de stock

        self.calcular_total()
        return True

    def registrar_pago(self) -> bool:
        if not self.confirmar_pedido():
            return False

        # Descontar stock
        for detalle in self._detalles:
            detalle.get_producto().descontar_stock(detalle.get_cantidad())

        self._estado_pago = "PAGADO"
        return True

    def despachar(self, operador: Trabajador) -> bool:
        """Regla 2: Bloquea despacho si el operador no tiene permisos o si no está PAGADO."""
        if not operador.puede_despachar():
            return False

        if self._estado_pago != "PAGADO":
            return False

        self._estado_entrega = "DESPACHADO"
        return True

    def procesar_despacho_entregas(self) -> list[dict]:
        """Ejecuta el polimorfismo de entrega para cada línea del pedido."""
        resultados = []
        for detalle in self._detalles:
            res = detalle.get_producto().procesar_entrega(detalle)
            resultados.append(res)
        return resultados

    def calcular_total(self) -> float:
        subtotal = sum(d.calcular_subtotal() for d in self._detalles)
        # Sumar fletes aplicables de productos físicos
        fletes = 0.0
        for d in self._detalles:
            p = d.get_producto()
            if isinstance(p, ProductoFisico):
                fletes += p.calcular_flete()
        self._total_flete_clp = fletes
        self._total_final_clp = subtotal + fletes
        return self._total_final_clp
