# INFORME DE PROPUESTA DE SOLUCIÓN: MODELO DE CLASES UML
## EVALUACIÓN SUMATIVA N°1 - UNIDAD 1

---

### 1. Portada e Integrantes

- **Institución:** INACAP
- **Carrera:** Ingeniería en Informática / Analista Programador
- **Asignatura:** Programación Orientada a Objeto Seguro
- **Código de Asignatura:** TI3V21 - PRIMAVERA 2026
- **Sección:** 114-2A-F2
- **Negocio Asignado:** 05 - Tienda de e-commerce (**ClickAndGo**)
- **Integrantes:**
  - Miguel Troncoso
  - [Nombre Segundo Integrante]
- **Docente:** [Nombre del Docente]
- **Fecha de Entrega:** Lunes 7 de septiembre de 2026, 20:30 horas
- **Nombre de Archivo:** `ES1_114-2A-F2_ecommerce.pdf`

---

### 2. El Problema en Nuestras Palabras (Resumen Ejecutivo)

La empresa **ClickAndGo** requiere una plataforma de comercio electrónico capaz de comercializar y procesar de forma automatizada y diferenciada tres tipos de productos en un mismo pedido (físicos con despacho y flete, digitales con entrega inmediata vía descarga sin costo de transporte, y servicios agendados para fechas futuras). La solución debe garantizar un estricto control de acceso basado en roles que restrinja al encargado de bodega a la preparación y despacho sin alterar precios ni catálogo, reservando dicha administración exclusivamente al administrador; asimismo, el sistema debe autenticar las compras exigiendo la validación formal de RUT chileno (mediante algoritmo Módulo 11) o correo electrónico, soportar pedidos multi-línea con sus cantidades consolidadas, salvaguardar la integridad del negocio impidiendo confirmar ventas sin stock disponible o despachar órdenes no pagadas, y calcular dinámicamente el precio en pesos de productos de electrónica importados cotizados en dólares según el tipo de cambio diario.

---

### 3. Diagrama de Clases UML

A continuación se presenta el diagrama de clases del sistema **ClickAndGo**, diseñado bajo el estándar formal UML, declarando visibilidad, tipos de datos en atributos, signaturas completas de métodos y simbología estricta para herencia, composición, agregación y asociaciones:

![Diagrama de Clases UML - Caso ClickAndGo](./diagrama_clases.png)

> **Nota de compatibilidad:** El archivo fuente editable para importar directamente en **draw.io** se encuentra respaldado en el repositorio bajo la ruta [`docs/diagrama_clases.drawio`](./diagrama_clases.drawio).

---

### 4. Explicación de Cada Clase

A continuación se detalla qué representa cada una de las once clases que componen el modelo, justificando su existencia a partir de las necesidades reales del negocio:

1. **`Cliente`:**  
   Representa a la persona natural o jurídica que realiza la compra dentro de la plataforma. Existe para encapsular la identidad del comprador, sus datos de contacto y la lógica de validación obligatoria de su identificador (RUT chileno validado por Módulo 11 o correo electrónico bajo estándar RFC), impidiendo que pedidos con datos inválidos ingresen al sistema comercial.

2. **`Pedido`:**  
   Representa la transacción comercial y contrato de compraventa consolidado entre el cliente y ClickAndGo. Existe para orquestar el ciclo de vida del pedido (controlando sus estados de pago y entrega), calcular los totales consolidados (subtotales y fletes) y resguardar las dos reglas de negocio más críticas: impedir la confirmación si falta stock en alguna línea y bloquear el despacho físico si la orden aún no ha sido pagada.

3. **`DetallePedido`:**  
   Representa cada una de las líneas de producto individuales incluidas dentro de un pedido específico. Existe para materializar la estructura transaccional multi-línea del negocio, almacenando la cantidad solicitada y congelando el precio unitario pactado al momento exacto de la compra, permitiendo calcular subtotales de forma independiente al catálogo vivo.

4. **`Producto` (`<<abstract>>`):**  
   Clase base abstracta que define la generalización y el contrato común de cualquier artículo comercializado por la tienda (`idProducto`, `nombre`, `precioBaseCLP`, `stock`). Existe para aplicar el principio de abstracción y polimorfismo, definiendo las operaciones abstractas `procesarEntrega()` y `calcularPrecioFinal()`, además de centralizar el control seguro y atómico del inventario (`descontarStock()` y `tieneStockSuficiente()`).

5. **`ProductoFisico`:**  
   Subclase especializada que modela aquellos productos tangibles (equipos, indumentaria, accesorios) que requieren transporte logístico terrestre o courier. Existe para registrar atributos físicos necesarios para el flete (`pesoKg`, `volumenM3`, `tarifaFleteBase`) y sobrescribir polimórficamente `procesarEntrega()`, calculando el costo del flete según distancia/destino y generando la guía de transporte correspondiente.

6. **`ProductoElectronica`:**  
   Subclase especializada que extiende de `ProductoFisico`. Modela artículos de tecnología e informática que son importados directamente desde el extranjero. Existe para satisfacer el requisito de precios dinámicos mediante su atributo `- precioUSD: float`, sobrescribiendo `calcularPrecioFinal(indicadorDolar: float)` para computar en tiempo real el precio de venta en pesos chilenos según la cotización del dólar observado del día.

7. **`ProductoDigital`:**  
   Subclase especializada que modela bienes intangibles como licencias de software, suscripciones o e-books. Existe para gestionar la entrega electrónica instantánea mediante enlaces seguros de descarga y claves de activación (`licenciaActivacion`), sobrescribiendo `procesarEntrega()` para emitir el acceso de manera inmediata tras la compra, con un flete de costo cero ($0 CLP) y sin requerir transporte.

8. **`ProductoServicio`:**  
   Subclase especializada que modela prestaciones y labores técnicas (tales como instalaciones a domicilio, ensamblaje o soporte postventa). Existe para gestionar la logística temporal de servicios, registrando la fecha y franja horaria agendada (`fechaAgendada`) y la dirección de visita, sobrescribiendo `procesarEntrega()` para reservar un cupo en la agenda del equipo técnico sin generar envíos de courier.

9. **`Trabajador` (`<<abstract>>`):**  
   Clase base abstracta que modela a los colaboradores internos de la empresa. Existe para estructurar el sistema de Control de Acceso Basado en Roles (RBAC), definiendo el contrato polimórfico de seguridad mediante los métodos abstractos `puedeModificarCatalogo(): bool` y `puedeDespachar(): bool`, asegurando que ninguna operación crítica se ejecute sin validar privilegios.

10. **`EncargadoBodega`:**  
    Subclase especializada de `Trabajador` que representa al personal de almacén y logística. Existe para modelar operativamente las funciones de preparación de paquetes y despacho (`puedeDespachar() == true`), garantizando por diseño del sistema que `puedeModificarCatalogo() == false`, lo que le impide tajantemente alterar precios o editar el catálogo de productos.

11. **`Administrador`:**  
    Subclase especializada de `Trabajador` que representa a los directivos o administradores del sistema. Existe para otorgar el control comercial pleno del negocio, permitiendo modificar el catálogo y ajustar los precios de venta de los productos (`puedeModificarCatalogo() == true`), así como supervisar o autorizar despachos globales (`puedeDespachar() == true`).

---

### 5. Justificación de las Relaciones y Multiplicidades

Para determinar con rigurosidad académica el tipo de relación y multiplicidad entre las clases, se aplicó la metodología formal vista en las sesiones 2 y 3: las **seis señales de identificación de clases** y el **árbol de decisión de dos preguntas** (*"¿Es un objeto de otro tipo?"*, y en caso negativo, *"¿El lado muchos acepta cero?"*).

#### 5.1. Jerarquías de Herencia (Generalización / Especialización - Símbolo: Triángulo Hueco)
*Pregunta clave:* **¿Es un objeto de otro tipo? -> SÍ.**
- **`Producto` <|-- `ProductoFisico`, `ProductoDigital`, `ProductoServicio`:**  
  Un producto físico, uno digital y un servicio de instalación **son tipos especializados de `Producto`**. Comparten la identidad, el nombre, el stock y el precio base, pero difieren en su comportamiento de entrega (`procesarEntrega()`), justificando la herencia y el polimorfismo.
- **`ProductoFisico` <|-- `ProductoElectronica`:**  
  Un artículo de electrónica importado **es un tipo de producto físico** (requiere transporte y flete), pero incorpora la particularidad comercial de cotizarse en dólares estadounidenses (`precioUSD`) y requerir el indicador de cambio del día para fijar su valor final en pesos.
- **`Trabajador` <|-- `EncargadoBodega`, `Administrador`:**  
  Tanto el encargado de bodega como el administrador **son tipos de trabajadores**. Comparten identidad y credenciales, pero especializan sus permisos de seguridad (`puedeModificarCatalogo()` y `puedeDespachar()`).

#### 5.2. Relación de Composición (Símbolo: Rombo Relleno `◆`)
*Preguntas:* ¿Es un objeto de otro tipo? -> NO. **¿El lado "muchos" acepta cero? -> NO.**
- **`Pedido` (1) ◆──────────── (1..*) `DetallePedido`:**  
  - **Tipo de relación:** Composición fuerte.
  - **Justificación existencial:** Una línea de detalle no posee sentido ni vida independiente fuera del pedido que la originó. Si se elimina o destruye un `Pedido`, todas sus líneas de detalle (`DetallePedido`) desaparecen físicamente con él.
  - **Multiplicidad (1 en Pedido, 1..* en DetallePedido):** Todo detalle pertenece obligatoriamente a exactamente **un (1)** pedido. Por otra parte, para que un pedido sea comercialmente válido y pueda existir, debe contener al menos una línea de producto (**1..***); no se admiten pedidos con cero líneas de detalle.

#### 5.3. Relación de Agregación (Símbolo: Rombo Hueco `◇`)
*Preguntas:* ¿Es un objeto de otro tipo? -> NO. **¿El lado "muchos" acepta cero? -> SÍ.**
- **`DetallePedido` (*) ◇──────────── (1) `Producto`:**  
  - **Tipo de relación:** Agregación por catálogo.
  - **Justificación existencial:** La línea de detalle hace referencia a un producto para conocer su descripción y descontar inventario, pero el ciclo de vida de ambos es completamente independiente. Si un pedido se anula o se borra una línea de detalle, el `Producto` correspondiente **continúa existiendo** en el catálogo general y en el inventario del negocio.
  - **Multiplicidad (* en DetallePedido, 1 en Producto):** Un producto del catálogo puede aparecer referenciado en cero, una o muchas líneas de detalle de distintos pedidos (**\***), mientras que cada línea de detalle referencia de manera unívoca a exactamente **un (1)** producto del catálogo.

#### 5.4. Relación de Asociación Directa y Dependencia
- **`Cliente` (1) ────────────> (0..*) `Pedido` (Asociación navegable "realiza"):**  
  - **Justificación:** Un cliente registrado en la base de datos puede ser un usuario recién creado que aún no efectúa compras (**0..*** pedidos), pero cada pedido emitido en el sistema debe estar indefectiblemente asociado a **un (1)** cliente identificado con RUT o correo electrónico válido.
- **`Pedido` ─ ─ ─ > `Trabajador` (Dependencia / Uso `«usa»`):**  
  - **Justificación:** La operación `despachar(operador: Trabajador)` recibe al trabajador en su parámetro para consultar en tiempo de ejecución si posee el privilegio `puedeDespachar() == true` antes de autorizar el cambio de estado.

---

### 6. Demostración de Cobertura de los Requisitos Mínimos (Rúbrica)

| Requisito Mínimo Declarado en la Ficha | Clase(s) y Miembro(s) Responsable(s) | Comportamiento Implementado en el Modelo |
| :--- | :--- | :--- |
| **1. Tres subtipos con un método que se comporta distinto en cada uno (Polimorfismo)** | • `ProductoFisico`<br>• `ProductoDigital`<br>• `ProductoServicio`<br>Método: `procesarEntrega(detalle)` | • `ProductoFisico`: Calcula flete terrestre según peso/volumen y emite orden a courier.<br>• `ProductoDigital`: Emite enlace de descarga instantáneo y clave de licencia ($0 flete).<br>• `ProductoServicio`: Agenda fecha y hora futura asignando técnico domiciliario. |
| **2. Dos tipos de trabajador con permisos distintos** | • `EncargadoBodega`<br>• `Administrador`<br>Métodos: `puedeModificarCatalogo()`, `puedeDespachar()` | • `EncargadoBodega`: `puedeModificarCatalogo() == false`, `puedeDespachar() == true`.<br>• `Administrador`: `puedeModificarCatalogo() == true`, `puedeDespachar() == true`, permitiendo editar precios y catálogo. |
| **3. Al menos un dato con validación obligatoria** | • `Cliente`<br>Método: `validarIdentificador(): bool` | Valida el formato y el dígito verificador del **RUT chileno mediante algoritmo Módulo 11** o el patrón sintáctico de **Correo Electrónico**, rechazando clientes con datos inválidos. |
| **4. Transacción con líneas de detalle** | • `Pedido` (Transacción)<br>• `DetallePedido` (Línea de detalle) | `Pedido` consolida el identificador, fecha, estados y totales, componiéndose de una o más instancias de `DetallePedido` (`1..*`) que congelan el precio unitario pactado y la cantidad. |
| **5. Dos reglas que impidan una operación (Invariantes del Negocio)** | • **Regla 1 (Stock):** `Pedido.confirmarPedido()`<br>• **Regla 2 (Despacho):** `Pedido.despachar(operador)` | • **Regla 1:** Se itera cada línea y se verifica `producto.tieneStockSuficiente(cantidad)`. Si algún ítem carece de stock, `confirmarPedido()` retorna `false` y aborta la transacción.<br>• **Regla 2:** `despachar()` valida que `operador.puedeDespachar() == true` **Y** `estadoPago == "PAGADO"`. Si el pedido aún no está pagado, se rechaza la operación. |
| **6. Precio dependiente de un indicador externo** | • `ProductoElectronica`<br>Método: `calcularPrecioFinal(indicadorDolar)` | Almacena el valor de importación en dólares (`- precioUSD: float`) y calcula dinámicamente el precio final en pesos chilenos multiplicando `precioUSD * indicadorDolar` del día. |

---

### 7. Conclusión

El modelo de clases propuesto para **ClickAndGo** resuelve integralmente la problemática expuesta en el enunciado sin incurrir en sobre-modelado ni clases huérfanas. Cada entidad posee responsabilidades bien delimitadas, comportamiento propio y atributos debidamente tipados y encapsulados. El uso de patrones de herencia y polimorfismo permite que la plataforma sea escalable (incorporando nuevos tipos de productos o trabajadores a futuro sin alterar la lógica de compras), mientras que la composición estricta y las reglas de validación en los métodos resguardan la seguridad y la consistencia transaccional del negocio.
