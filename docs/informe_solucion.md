# INFORME DE PROPUESTA DE SOLUCIÓN: MODELO DE CLASES UML
## EVALUACIÓN SUMATIVA N°1 - UNIDAD 1

---

### 1. Portada e Integrantes

- **Institución:** INACAP
- **Carrera:** Analista Programador
- **Asignatura:** Programación Orientada a Objetos
- **Código de Asignatura:** TI3V21 - PRIMAVERA 2026
- **Sección:** 114-2A-F2
- **Negocio Asignado:** 05: Tienda de e-commerce (**ClickAndGo**)
- **Integrantes del Equipo:**
  1. Miguel Troncoso
  2. Alexandy Remicinthe
- **Docente a Cargo:** Michael Alexis Arjel Mayerovich
- **Fecha y Hora de Entrega:** Lunes 7 de septiembre de 2026, 20:30 horas
- **Nombre de Archivo Oficial:** `ES1_114-2A-F2_ecommerce.pdf`

---

### 2. El Problema en Nuestras Palabras (Resumen Ejecutivo)

La empresa **ClickAndGo** comercializa productos bajo tres mecánicas de entrega diferenciadas en un mismo pedido comercial (bienes físicos despachados por transporte con cálculo de flete, bienes digitales con entrega instantánea mediante enlaces o claves de activación sin flete, y servicios técnicos agendados para fechas futuras). Para operar de forma segura, el negocio requiere una arquitectura de software con control de acceso basado en roles que impida al encargado de bodega modificar precios o el catálogo limitándolo exclusivamente a la preparación y despacho, resguardando la gestión de precios únicamente para el administrador. Asimismo, el sistema exige la validación formal de clientes mediante RUT chileno (con algoritmo Módulo 11) o correo electrónico antes de admitir cualquier compra, consolida transacciones multi-línea congelando cantidades y precios pactados, y protege la integridad operativa bloqueando la confirmación de pedidos que carezcan de stock suficiente o el despacho de órdenes que aún no hayan sido pagadas, incorporando adicionalmente la conversión dinámica de precios en dólares a pesos chilenos para artículos de electrónica importados.

---

### 3. Diagrama de Clases UML

A continuación se presenta el diagrama de clases del sistema **ClickAndGo**, diseñado bajo el estándar formal UML, declarando visibilidad, tipos de datos en atributos, signaturas completas de métodos y simbología estricta para herencia, composición, agregación y asociaciones:

![Diagrama de Clases UML - Caso ClickAndGo](./diagrama_clases.png)

> **Nota de compatibilidad:** El archivo fuente editable para importar directamente en **draw.io** se encuentra respaldado en el repositorio bajo la ruta [`docs/diagrama_clases.drawio`](./diagrama_clases.drawio).

---

### 4. Explicación de Cada Clase

A continuación se detalla qué representa cada una de las once clases que componen el modelo, justificando su existencia a partir de las necesidades reales del negocio:

1. **`Cliente`:**  
   Modela al usuario o comprador de la tienda. Existe para registrar su identidad y centralizar la regla de validación de ingreso (RUT chileno mediante algoritmo Módulo 11 o correo electrónico sintáctico), impidiendo que transacciones asociadas a datos inválidos sean procesadas en la plataforma.

2. **`Pedido`:**  
   Representa la transacción comercial y contrato de compraventa entre el cliente y ClickAndGo. Orquesta los estados de pago y despacho, totaliza los valores monetarios de la compra (incluyendo flete) y salvaguarda las invariantes de negocio: no confirma pedidos sin stock y bloquea el despacho de pedidos no pagados.

3. **`DetallePedido`:**  
   Modela cada línea de producto adquirida dentro de un pedido. Existe para resolver transacciones multi-línea, encapsulando la cantidad solicitada y congelando el precio unitario pactado al momento de la venta, garantizando la inmutabilidad histórica del subtotal frente a futuros cambios de catálogo.

4. **`Producto` (`<<abstract>>`):**  
   Clase base abstracta que define la generalización y el contrato común de cualquier ítem en inventario (identificador, nombre, stock y precio base). Define las operaciones polimórficas abstractas `procesarEntrega()` y `calcularPrecioFinal()`, y encapsula las rutinas de descuento y verificación de stock.

5. **`ProductoFisico`:**  
   Subclase especializada que modela bienes tangibles que requieren despacho mediante empresas de transporte. Incorpora atributos físicos (peso, volumen y tarifa base) y sobrescribe `procesarEntrega()` para calcular el flete logístico y generar la orden de courier.

6. **`ProductoElectronica`:**  
   Subclase que extiende de `ProductoFisico` para modelar artículos importados de tecnología. Existe para cumplir el requisito de precios dependientes de indicadores externos: mantiene su costo de origen en dólares (`- precioUSD`) y sobrescribe `calcularPrecioFinal()` multiplicándolo por el valor del dólar del día.

7. **`ProductoDigital`:**  
   Subclase especializada que modela bienes intangibles como licencias o e-books. Gestiona la entrega inmediata sin costo de transporte ($0 flete), emitiendo el enlace seguro de descarga y la clave de activación al momento de la compra.

8. **`ProductoServicio`:**  
   Subclase que modela prestaciones profesionales o técnicas (instalaciones a domicilio). Gestiona la logística temporal del servicio, registrando la fecha/hora agendada y la dirección del cliente, asignando el técnico sin generar transporte de carga.

9. **`Trabajador` (`<<abstract>>`):**  
   Clase base abstracta para el personal de la empresa. Modela el control de acceso basado en roles (RBAC) mediante los métodos abstractos `puedeModificarCatalogo()` y `puedeDespachar()`, protegiendo las operaciones críticas del sistema.

10. **`EncargadoBodega`:**  
    Subclase de `Trabajador` que modela al personal de almacén. Permite preparar y despachar pedidos (`puedeDespachar() == true`), pero tiene prohibido por diseño alterar precios o catálogo (`puedeModificarCatalogo() == false`).

11. **`Administrador`:**  
    Subclase de `Trabajador` que modela la gerencia y supervisión. Posee facultades plenas en la plataforma: gestiona el catálogo, modifica precios y cuenta con autorización de despacho.

---

### 5. Justificación de las Relaciones y Multiplicidades

Para determinar con rigurosidad académica el tipo de relación y multiplicidad entre las clases, se aplicó la metodología formal vista en las sesiones 2 y 3: las **seis señales de identificación de clases** y el **árbol de decisión de dos preguntas** (*"¿Es un objeto de otro tipo?"*, y en caso negativo, *"¿El lado muchos acepta cero?"*).

#### 5.1. Jerarquías de Herencia (Triángulo Hueco — Pregunta 1: ¿Es un objeto de otro tipo? → SÍ)
- **`Producto` <|-- `ProductoFisico`, `ProductoDigital`, `ProductoServicio`:**  
  Un producto físico, uno digital y un servicio de instalación *son tipos especializados de `Producto`*. Comparten atributos de catálogo e inventario pero resuelven polimórficamente su entrega.
- **`ProductoFisico` <|-- `ProductoElectronica`:**  
  Un artículo de electrónica importado *es un tipo de `ProductoFisico`* (requiere transporte), pero añade la lógica financiera de cotizarse en USD y convertirse con la tasa cambiaria del día.
- **`Trabajador` <|-- `EncargadoBodega`, `Administrador`:**  
  Tanto el bodeguero como el administrador *son tipos de `Trabajador`* que especializan sus permisos operativos.

#### 5.2. Composición (Rombo Relleno — Pregunta 2: ¿El lado muchos acepta cero? → NO)
- **`Pedido` (1) [Composición: rombo relleno] ------------> (1..*) `DetallePedido`:**  
  Existe una dependencia existencial fuerte: una línea de detalle no puede existir en el mundo real sin pertenecer a un pedido. Si el pedido se elimina, sus líneas se destruyen. Además, el lado "muchos" **no acepta cero**: un pedido requiere al menos una línea comercial válida (**1..***) para existir.

#### 5.3. Agregación (Rombo Hueco — Pregunta 2: ¿El lado muchos acepta cero? → SÍ)
- **`DetallePedido` (*) [Agregación: rombo hueco] ------------> (1) `Producto`:**  
  La línea de detalle referencia al producto para registrar qué se vendió, pero sus ciclos de vida son independientes. Si se elimina el detalle o se anula la orden, el **Producto permanece intacto** en el catálogo. Un producto puede aparecer en 0 o muchas líneas (**\***) de distintos pedidos.

#### 5.4. Asociación Directa y Dependencia
- **`Cliente` (1) ------------------------> (0..*) `Pedido`:** Un cliente registrado puede no registrar compras aún (**0..***), pero cada pedido emitido pertenece forzosamente a exactamente un cliente (**1**).
- **`Pedido` · · · > `Trabajador` (`«usa»`):** La operación `despachar(operador: Trabajador)` recibe al trabajador como parámetro para verificar en tiempo de ejecución si cuenta con el permiso legal de despacho.

---

### 6. Matriz de Cumplimiento de los 6 Requisitos Mínimos de la Ficha

| Requisito de la Ficha | Clases y Miembros Responsables | Demostración de Cumplimiento |
| :--- | :--- | :--- |
| **1. Tres subtipos con polimorfismo** | `ProductoFisico`<br>`ProductoDigital`<br>`ProductoServicio` | Implementan `procesarEntrega()` según el tipo: flete logístico, enlace de descarga o reserva en agenda. |
| **2. Dos trabajadores con permisos distintos** | `EncargadoBodega`<br>`Administrador` | Bodega solo despacha (`puedeModificarCatalogo=false`); Administrador gestiona precios y catálogo. |
| **3. Dato con validación obligatoria** | `Cliente.validarIdentificador()` | Valida algoritmo Módulo 11 (RUT chileno) o formato de Correo Electrónico antes de aceptar el pedido. |
| **4. Transacción con líneas de detalle** | `Pedido` [Composición] `DetallePedido` | Multi-línea (1 a 1..*), congelando cantidad y precio pactado al momento de la compra. |
| **5. Dos reglas que impidan una operación** | • `confirmarPedido()`<br>• `despachar()` | • Regla 1: Bloquea confirmación si no hay stock suficiente.<br>• Regla 2: Bloquea despacho si el pedido no está PAGADO. |
| **6. Precio con indicador externo** | `ProductoElectronica.calcularPrecioFinal()` | Convierte el costo base en USD a pesos chilenos multiplicando por la tasa del dólar observado del día. |

---

### 7. Conclusión y Veredicto Técnico

El modelo de clases propuesto para **ClickAndGo** satisface con máxima rigurosidad técnica los criterios de evaluación de la Unidad 1. Se aplican los cuatro pilares fundamentales de la POO (Abstracción, Encapsulamiento, Herencia y Polimorfismo), se diferencian conceptualmente las relaciones de composición y agregación mediante el árbol de decisiones pedagógico, y se salvaguardan las reglas de negocio de la empresa, sentando una base sólida y extensible para su posterior codificación e integración.
