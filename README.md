# ClickAndGo - Sistema de gestion E-commerce

[![INACAP](https://img.shields.io/badge/INACAP-TI3V21-CC0000?style=flat-square)](https://www.inacap.cl/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Persistencia-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Demo](https://img.shields.io/badge/Demo-inacap.superflash.site-1C4E80?style=flat-square)](https://inacap.superflash.site)

Sistema desarrollado para la asignatura **Programacion Orientada a Objeto Seguro (TI3V21)**
de INACAP, **Evaluacion Sumativa N2** (Unidades 2 y 3: software orientado a objetos,
persistencia y seguridad en Python).

---

## 1. Integrantes y negocio

| Dato | Valor |
| :--- | :--- |
| Institucion | Instituto Profesional INACAP, Sede Puente Alto |
| Carrera | Ingenieria Informatica |
| Asignatura | Programacion Orientada a Objeto Seguro - TI3V21 (Primavera 2026) |
| Seccion | 114-2A-F2 |
| Docente | Michael Arjel |
| Caso asignado | 05 - Tienda de e-commerce: **ClickAndGo** |
| Integrantes | **Miguel Troncoso** y **Alexandy Remicinthe** |
| Entrega | Miercoles 7 de octubre de 2026, 19:50 hrs |
| Repositorio | https://github.com/MiguelTroncoso/ecommerce |
| Demostracion en linea | https://inacap.superflash.site |

### El negocio

**ClickAndGo** vende tres mecanicas de entrega distintas dentro de un mismo pedido:

1. **Productos fisicos**: se despachan por transporte terrestre y pagan flete calculado por peso,
   volumen y distancia.
2. **Productos digitales**: se entregan al instante con un enlace de descarga y una licencia, sin
   costo de despacho.
3. **Servicios**: se agendan para una fecha y hora futura en la direccion del cliente.
4. **Electronica importada**: producto fisico cotizado en dolares, cuyo precio en pesos depende del
   valor del dolar observado del dia (indicador externo).

### Roles operativos (RBAC)

| Rol | Modificar catalogo | Despachar pedidos |
| :--- | :---: | :---: |
| `Administrador` | Si | Si |
| `EncargadoBodega` | **No** | Si |

---

## 2. Como instalar y ejecutar

Requisitos: **Python 3.11 o superior**. No se necesita instalar ni configurar ninguna base de
datos: el programa crea el archivo SQLite y sus tablas la primera vez que se ejecuta.

```bash
git clone https://github.com/MiguelTroncoso/ecommerce.git
cd ecommerce

# 1. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el programa
python main.py
```

Al iniciar aparece el menu principal:

```
==============================================================================
  MENU PRINCIPAL
==============================================================================
  1. Gestionar clientes
  2. Gestionar productos (catalogo)
  3. Gestionar pedidos (transacciones)
  4. Calcular precio con el dolar del dia (mindicador.cl)
  5. Ver trabajadores y permisos (RBAC)
  6. Iniciar sesion / cambiar operador
  7. Cargar datos de demostracion
  0. Salir
```

### Credenciales de demostracion

| Rol | Usuario | Contrasena |
| :--- | :--- | :--- |
| Administrador | `Maria Gonzalez` | `admin1234` |
| Encargado de bodega | `Juan Perez` | `bodega1234` |

La sesion comienza como **Administrador** para facilitar la demostracion; desde la opcion 6 se puede
cambiar de operador y comprobar que el encargado de bodega **no** puede modificar el catalogo.

### Otros comandos utiles

```bash
python demo.py                       # Demostracion automatica de los 6 requisitos
python tests/test_guion_pruebas.py   # Guion de pruebas P01 a P19
```

---

## 3. Arquitectura del proyecto

```
ecommerce/
  main.py                 Menu de consola (punto de entrada)
  demo.py                 Demostracion automatica de la rubrica
  requirements.txt        Dependencias del sistema de consola
  model/                  Clases del negocio, una por archivo
  dao/                    Persistencia SQLite con consultas parametrizadas
  servicios/              Validacion de entradas y API mindicador.cl
  tests/                  Guion de pruebas automatizado
  web/                    Sitio de documentacion y consola en vivo (subdominio)
  docs/                   Informes PDF, diagrama UML y evidencias
  datos/                  Base de datos SQLite (se genera en tiempo de ejecucion)
```

### Modelo (`model/`)

| Archivo | Clase | Responsabilidad |
| :--- | :--- | :--- |
| `cliente.py` | `Cliente` | Identidad del comprador y validacion obligatoria de RUT/Email |
| `producto.py` | `Producto` (ABC) | Contrato del catalogo y del inventario |
| `producto_fisico.py` | `ProductoFisico` | Despacho por transporte y calculo de flete |
| `producto_electronica.py` | `ProductoElectronica` | Importado en USD; hereda de `ProductoFisico` |
| `producto_digital.py` | `ProductoDigital` | Entrega instantanea con enlace y licencia |
| `producto_servicio.py` | `ProductoServicio` | Agenda una visita tecnica futura |
| `detalle_pedido.py` | `DetallePedido` | Linea de la transaccion con precio congelado |
| `pedido.py` | `Pedido` | Transaccion y reglas de negocio |
| `trabajador.py` | `Trabajador` (ABC) | Personal, autenticacion y permisos |
| `encargado_bodega.py` | `EncargadoBodega` | Despacha, no modifica catalogo |
| `administrador.py` | `Administrador` | Control total del catalogo |
| `excepciones.py` | Excepciones | Una excepcion propia por cada regla de negocio |

Los subtipos heredan con `super().__init__()` y sobrescriben `procesar_entrega()`; los atributos son
privados y se exponen con `property`, validando en el *setter*.

### Persistencia (`dao/`)

| Archivo | Contenido |
| :--- | :--- |
| `conexion.py` | Conexion SQLite, creacion automatica del esquema y ejecucion parametrizada |
| `cliente_dao.py` | CRUD de clientes |
| `producto_dao.py` | CRUD del catalogo y reconstruccion polimorfica de cada subtipo |
| `pedido_dao.py` | Insercion atomica del pedido con sus lineas de detalle |
| `trabajador_dao.py` | Usuarios, roles y autenticacion |

Tablas: `trabajadores`, `clientes`, `productos`, `pedidos`, `detalle_pedido` y `configuracion`.
Todas se crean al iniciar el programa (`conexion.crear_tablas()`).

### Servicios (`servicios/`)

* `validador.py`: validacion de tipo, formato y rango de **todas** las entradas del usuario.
* `indicador_dolar.py`: consumo de `https://mindicador.cl/api/dolar` con `requests` y `timeout=5`,
  con respaldo local del ultimo valor conocido.
* `inicializacion.py`: creacion del esquema y carga de datos iniciales.

---

## 4. Decisiones de seguridad

### 4.1 Inyeccion SQL

**Riesgo:** si el texto que escribe el usuario se concatena dentro de una sentencia SQL, un valor
como `'; DROP TABLE productos; --` podria alterar la base de datos.

**Decision:** absolutamente todas las consultas usan **parametros enlazados** (`?` o `:nombre`).
Nunca se construye SQL con concatenacion ni con f-strings. Los nombres de columna son fijos y
definidos por el programador, por lo que tampoco son manipulables.

```python
# dao/cliente_dao.py
self._bd.consultar_uno(
    "SELECT * FROM clientes WHERE id_cliente = :id",
    {"id": id_cliente},
)
```

La conexion ademas activa `PRAGMA foreign_keys = ON` para que las claves foraneas se respeten y el
pedido no pueda quedar con lineas huerfanas.

### 4.2 Validacion de entradas

**Decision:** cada dato se valida **antes de usarse**, por tipo, formato y rango.

* En el modelo, los *setters* validan y lanzan la excepcion correspondiente:
  `Cliente.identificador` (RUT Modulo 11 o correo), `Producto.stock` (entero no negativo),
  `Producto.precio_base_clp` (no negativo), `ProductoServicio.fecha_agendada` (fecha futura), etc.
* En la consola, `servicios/validador.py` pide el dato en un bucle: si es invalido muestra el
  mensaje y vuelve a preguntar, sin detener el programa (casos P08 y P19 del guion de pruebas).

```python
def pedir_entero(mensaje, leer_entrada=input, minimo=None, maximo=None) -> int:
    while True:
        try:
            return validar_entero(leer_entrada(f"{mensaje}: "), minimo, maximo)
        except DatoInvalidoError as error:
            print(f"  [!] {error} Intente nuevamente.")
```

### 4.3 Autenticacion y permisos (RBAC)

**Decision:** las contrasenas se guardan con **PBKDF2-HMAC-SHA256**, 120.000 iteraciones y un *salt*
aleatorio por usuario (`os.urandom(16)`); la comparacion usa `hmac.compare_digest` para evitar
ataques de temporizacion. Los permisos se resuelven por polimorfismo
(`puede_modificar_catalogo()`, `puede_despachar()`) y una accion no autorizada lanza
`SinPermisoError`.

### 4.4 Manejo de errores y excepciones propias

**Decision:** cada regla de negocio que impide una operacion tiene su **excepcion propia**, se lanza
desde el metodo que corresponde y se captura de forma **especifica** en `main.py`:

| Excepcion | Regla que protege |
| :--- | :--- |
| `StockInsuficienteError` | Regla 1: no confirmar un pedido sin stock |
| `PedidoNoPagadoError` | Regla 2: no despachar un pedido impago |
| `SinPermisoError` | RBAC: el rol no tiene autorizacion |
| `IdentificadorInvalidoError` | RUT o correo invalido |
| `IndicadorNoDisponibleError` | La API externa no responde |
| `DatoInvalidoError` | Entrada con tipo, formato o rango incorrecto |

### 4.5 Consumo de servicios externos

**Decision:** la consulta a `mindicador.cl` usa la libreria oficial `requests` con
`timeout=5`, valida el codigo HTTP con `raise_for_status()`, valida que la respuesta traiga la serie
del dolar y guarda el ultimo valor conocido en `datos/dolar_respaldo.json`. Si la API falla, el
sistema informa el problema y sigue funcionando con el ultimo valor (caso P17).

---

## 5. Uso de herramientas de IA: que se adopto, que se modifico y que se descarto

### 5.1 Ejemplo concreto adoptado

**Sugerencia de la IA:** usar `sqlite3.Row` como `row_factory` y reemplazar los accesos por indice
(`fila[0]`, `fila[3]`) por accesos por nombre de columna.

**Decision: ADOPTADO.** El codigo original del equipo usaba indices numericos, lo que volvia muy
fragil cualquier cambio de columnas. Se adopto el `row_factory` y las consultas ahora leen por
nombre:

```python
# dao/conexion.py
conexion = sqlite3.connect(str(self._ruta))
conexion.row_factory = sqlite3.Row
conexion.execute("PRAGMA foreign_keys = ON;")
```

*Razon tecnica:* el codigo queda autoexplicativo y un cambio de orden en el `SELECT` ya no altera la
construccion de los objetos.

### 5.2 Ejemplo concreto modificado

**Sugerencia de la IA:** implementar el timeout de la API asi:

```python
respuesta = requests.get(URL)          # sugerencia original de la IA
```

**Decision: MODIFICADO.** Se conservo la idea de usar `requests`, pero se agrego el tiempo maximo de
espera y el manejo de cada falla concreta, porque la version sugerida dejaba el programa colgado si
el servidor no respondia:

```python
respuesta = requests.get(self._url, timeout=self._timeout)
respuesta.raise_for_status()
...
except (requests.RequestException, ValueError, KeyError, TypeError) as error:
    raise IndicadorNoDisponibleError(...) from error
```

*Razon tecnica:* el criterio 3.1.3 exige tiempo maximo de espera y continuidad del sistema. Ademas se
separo `requests.RequestException` (falla de red) de `ValueError`/`KeyError` (respuesta inesperada),
para no ocultar el error con un `except` generico.

### 5.3 Ejemplo concreto descartado

**Sugerencia de la IA:** resolver el tipo de producto con una estructura `if/elif` sobre el campo
`tipo` dentro de `Pedido.procesar_despacho_entregas()`:

```python
# Sugerencia descartada
for detalle in self._detalles:
    if detalle.producto.tipo == "FISICO":
        ...
    elif detalle.producto.tipo == "DIGITAL":
        ...
```

**Decision: DESCARTADO.** En su lugar se mantiene el polimorfismo: cada subtipo sobrescribe
`procesar_entrega()` y el pedido solo invoca el metodo.

```python
def procesar_despacho_entregas(self) -> list[dict]:
    return [detalle.producto.procesar_entrega(detalle) for detalle in self._detalles]
```

*Razon tecnica:* la rubrica del criterio 2.1.2 indica explicitamente que reemplazar el polimorfismo
por `if` sobre el tipo queda en nivel "En desarrollo". Con el polimorfismo, agregar un nuevo tipo de
producto no obliga a modificar `Pedido` (principio Abierto/Cerrado).

### 5.4 Otras decisiones descartadas

| Sugerencia de la IA | Decision | Razon tecnica |
| :--- | :--- | :--- |
| Guardar la contrasena con `hashlib.md5()` | Descartada | MD5 no es apto para contrasenas; se uso PBKDF2-HMAC-SHA256 con salt |
| Usar `except Exception: pass` en la API | Descartada | Oculta el error; se capturan excepciones concretas y se informa |
| Guardar los pedidos en una lista en memoria | Descartada | La rubrica exige persistencia real en base de datos |

---

## 6. Cumplimiento de los requisitos de la ficha del negocio

| # | Requisito | Implementacion | Evidencia |
| :-: | :--- | :--- | :--- |
| 1 | Tres subtipos con un metodo que cambia | `ProductoFisico`, `ProductoDigital`, `ProductoServicio` sobrescriben `procesar_entrega()` | Opcion 3 > 7 del menu; prueba P09-P11 |
| 2 | Dos trabajadores con permisos distintos | `Administrador` y `EncargadoBodega` | Opcion 5 del menu; inicio de sesion como bodega |
| 3 | Un dato con validacion obligatoria | `Cliente.identificador`: RUT Modulo 11 o correo | Opcion 1 > 1; pruebas P07-P08 |
| 4 | Una transaccion con lineas de detalle | `Pedido` compone `DetallePedido` (1 a 1..*) | Opcion 3 > 1 y 3; pruebas P12-P13 |
| 5 | Dos reglas que impidan una operacion | `StockInsuficienteError` y `PedidoNoPagadoError` | Opciones 4 y 6 del submenu pedidos; P14-P15 |
| 6 | Un precio con indicador externo | `ProductoElectronica` con `mindicador.cl` | Opcion 4 del menu; pruebas P16-P17 |

---

## 7. Guion de pruebas

Los 19 casos del guion de pruebas estan automatizados en `tests/test_guion_pruebas.py`:

```bash
python tests/test_guion_pruebas.py
```

Cobertura: ejecucion y menu (P01), CRUD (P02-P06), validacion del dato obligatorio (P07-P08),
entrega polimorfica por tipo (P09-P11), transaccion multi-linea y detalle (P12-P13), las dos reglas
de negocio (P14-P15), indicador del dolar y su falla (P16-P17) y estabilidad ante entradas invalidas
(P18-P19).

---

## 8. Publicacion web (valor agregado)

Ademas del programa de consola exigido por la evaluacion, el proyecto se publica en
**https://inacap.superflash.site** con:

* documentacion del proyecto desde cero para el cliente;
* recorrido del codigo por archivo;
* resultados del guion de pruebas;
* **consola en vivo** que ejecuta el mismo `main.py` en un entorno aislado por visitante.

```bash
pip install -r web/requirements.txt
python web/app.py                  # http://127.0.0.1:3030
```

---

## 9. Documentos de entrega

| Documento | Contenido |
| :--- | :--- |
| [`docs/ES2_114-2A-F2_ecommerce.pdf`](docs/ES2_114-2A-F2_ecommerce.pdf) | Informe tecnico de la solucion y matriz de la rubrica |
| [`docs/GUIA_CLIENTE_ClickAndGo.pdf`](docs/GUIA_CLIENTE_ClickAndGo.pdf) | Guia del cliente: el proyecto y el codigo explicados desde cero |
| [`docs/diagrama_clases.drawio`](docs/diagrama_clases.drawio) | Diagrama de clases UML editable |
| [`docs/diagrama_clases.png`](docs/diagrama_clases.png) | Diagrama de clases en imagen |

---

**Repositorio:** https://github.com/MiguelTroncoso/ecommerce
**Demo:** https://inacap.superflash.site
