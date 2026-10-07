#!/usr/bin/env python3
"""Genera los dos documentos PDF de entrega de ClickAndGo.

1. ES2_114-2A-F2_ecommerce.pdf  -> Informe tecnico de la solucion.
2. GUIA_CLIENTE_ClickAndGo.pdf  -> Guia del cliente desde cero (proyecto y codigo).

Uso:

    python docs/build_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

DIR_DOCS = Path(__file__).resolve().parent
AZUL = colors.HexColor("#0D233A")
AZUL_CLARO = colors.HexColor("#1C4E80")
ACENTO = colors.HexColor("#D63426")
GRIS = colors.HexColor("#F2F5F9")
BORDE = colors.HexColor("#D6DEE8")
VERDE = colors.HexColor("#1A7F4B")
TEXTO = colors.HexColor("#1F2933")


# ----------------------------------------------------------------------
# Plantilla con encabezado y pie de pagina
# ----------------------------------------------------------------------
class DocumentoClickAndGo(BaseDocTemplate):
    def __init__(self, ruta: str, titulo_documento: str, **kwargs) -> None:
        self.titulo_documento = titulo_documento
        super().__init__(
            ruta,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=22 * mm,
            bottomMargin=18 * mm,
            title=titulo_documento,
            author="Miguel Troncoso y Alexandy Remicinthe",
            subject="INACAP TI3V21 - Evaluacion Sumativa N2",
            **kwargs,
        )
        alto = A4[1] - 42 * mm
        marco = Frame(20 * mm, 18 * mm, A4[0] - 40 * mm, alto, id="normal")
        self.addPageTemplates([PageTemplate(id="principal", frames=[marco], onPage=self._decorar)])

    def _decorar(self, lienzo: canvas.Canvas, documento) -> None:
        numero = documento.page
        if numero == 1:
            return
        lienzo.saveState()
        lienzo.setStrokeColor(BORDE)
        lienzo.setLineWidth(0.6)
        lienzo.line(20 * mm, A4[1] - 15 * mm, A4[0] - 20 * mm, A4[1] - 15 * mm)
        lienzo.setFont("Helvetica", 8)
        lienzo.setFillColor(colors.HexColor("#667788"))
        lienzo.drawString(20 * mm, A4[1] - 13 * mm, self.titulo_documento)
        lienzo.drawRightString(A4[0] - 20 * mm, A4[1] - 13 * mm, "INACAP - TI3V21")
        lienzo.line(20 * mm, 14 * mm, A4[0] - 20 * mm, 14 * mm)
        lienzo.setFont("Helvetica", 8)
        lienzo.drawString(20 * mm, 10 * mm, "ClickAndGo - Caso 05: Tienda de e-commerce")
        lienzo.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Pagina {numero}")
        lienzo.restoreState()


# ----------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------
def crear_estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "cubierta_titulo": ParagraphStyle(
            "cubierta_titulo", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=30, leading=34, textColor=AZUL, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cubierta_sub": ParagraphStyle(
            "cubierta_sub", parent=base["Normal"], fontName="Helvetica", fontSize=13,
            leading=19, textColor=AZUL_CLARO, alignment=TA_CENTER, spaceAfter=4,
        ),
        "cubierta_dato": ParagraphStyle(
            "cubierta_dato", parent=base["Normal"], fontName="Helvetica", fontSize=10.5,
            leading=16, textColor=TEXTO, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16,
            leading=20, textColor=AZUL, spaceBefore=16, spaceAfter=8,
        ),
        "cubierta_documento": ParagraphStyle(
            "cubierta_documento", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, leading=20, textColor=ACENTO, alignment=TA_CENTER,
            spaceBefore=2, spaceAfter=2,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
            leading=16, textColor=AZUL_CLARO, spaceBefore=13, spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.8,
            leading=14, textColor=AZUL, spaceBefore=9, spaceAfter=4,
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo", parent=base["BodyText"], fontName="Helvetica", fontSize=10,
            leading=15, textColor=TEXTO, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "vineta": ParagraphStyle(
            "vineta", parent=base["BodyText"], fontName="Helvetica", fontSize=10,
            leading=14.5, textColor=TEXTO, leftIndent=12, bulletIndent=2, spaceAfter=3,
        ),
        "celda": ParagraphStyle(
            "celda", parent=base["Normal"], fontName="Helvetica", fontSize=8.4,
            leading=11.4, textColor=TEXTO,
        ),
        "celda_encabezado": ParagraphStyle(
            "celda_encabezado", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.6, leading=11.6, textColor=colors.white,
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName="Courier", fontSize=7.9,
            leading=10.6, textColor=colors.HexColor("#0D233A"),
            backColor=colors.HexColor("#F4F7FB"), borderPadding=6,
            leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=9.4,
            leading=13.4, textColor=colors.HexColor("#5A4A00"), backColor=colors.HexColor("#FFF8E6"),
            borderPadding=7, alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=8,
        ),
        "leyenda": ParagraphStyle(
            "leyenda", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=8.4,
            leading=11, textColor=colors.HexColor("#667788"), alignment=TA_CENTER,
            spaceBefore=3, spaceAfter=10,
        ),
    }


def tabla(datos: list[list], anchos: list[float] | None = None, alineaciones=None) -> Table:
    tabla_ = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if alineaciones:
        for indice, alineacion in enumerate(alineaciones):
            estilo.append(("ALIGN", (indice, 1), (indice, -1), alineacion))
    tabla_.setStyle(TableStyle(estilo))
    return tabla_


def celdas(filas: list[list[str]], estilos: dict, primera_fila_encabezado: bool = True) -> list[list]:
    resultado = []
    for indice, fila in enumerate(filas):
        estilo = estilos["celda_encabezado"] if (indice == 0 and primera_fila_encabezado) else estilos["celda"]
        resultado.append([Paragraph(str(celda), estilo) for celda in fila])
    return resultado


def cubierta(estilos: dict, titulo: str, subtitulo: str, datos: list[tuple[str, str]]) -> list:
    elementos = [
        Spacer(1, 26 * mm),
        Paragraph("ClickAndGo", estilos["cubierta_titulo"]),
        Paragraph(subtitulo, estilos["cubierta_sub"]),
        Spacer(1, 6 * mm),
        Paragraph(titulo, estilos["cubierta_documento"]),
        Spacer(1, 8 * mm),
    ]
    filas = [[Paragraph(f"<b>{etiqueta}</b>", estilos["celda"]), Paragraph(valor, estilos["celda"])]
             for etiqueta, valor in datos]
    tabla_datos = Table(filas, colWidths=[45 * mm, 100 * mm], hAlign="CENTER")
    tabla_datos.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDE),
        ("TEXTCOLOR", (0, 0), (0, -1), AZUL_CLARO),
    ]))
    elementos += [tabla_datos, PageBreak()]
    return elementos


def imagen_diagrama(ancho_maximo: float = 165 * mm):
    ruta = DIR_DOCS / "diagrama_clases.png"
    if not ruta.exists():
        return Spacer(1, 1)
    ancho, alto = ImageReader(str(ruta)).getSize()
    escala = min(ancho_maximo / ancho, 1.0)
    return Image(str(ruta), width=ancho * escala, height=alto * escala)


# ----------------------------------------------------------------------
# Documento 1: informe tecnico de la solucion
# ----------------------------------------------------------------------
def build_informe(ruta_salida: Path) -> None:
    estilos = crear_estilos()
    documento = DocumentoClickAndGo(
        str(ruta_salida), "Informe tecnico - Evaluacion Sumativa N2 (TI3V21)"
    )
    e = estilos
    contenido: list = []

    contenido += cubierta(
        e,
        "Documento tecnico de la solucion",
        "Evaluacion Sumativa N2 - Unidades 2 y 3<br/>Software orientado a objetos, persistencia y seguridad en Python",
        [
            ("Institucion", "Instituto Profesional INACAP - Sede Puente Alto"),
            ("Carrera", "Ingenieria Informatica"),
            ("Asignatura", "Programacion Orientada a Objeto Seguro - TI3V21"),
            ("Seccion", "114-2A-F2 - Primavera 2026"),
            ("Negocio asignado", "05 - Tienda de e-commerce: ClickAndGo"),
            ("Integrantes", "Miguel Troncoso<br/>Alexandy Remicinthe"),
            ("Docente", "Michael Arjel"),
            ("Fecha de entrega", "Miercoles 7 de octubre de 2026, 19:50 hrs"),
            ("Repositorio", "https://github.com/MiguelTroncoso/ecommerce"),
            ("Demostracion en linea", "https://inacap.superflash.site"),
        ],
    )

    contenido += [
        Paragraph("1. Resumen ejecutivo", e["h1"]),
        Paragraph(
            "ClickAndGo es una tienda de comercio electronico que vende, dentro de un mismo pedido, "
            "productos fisicos, productos digitales, servicios tecnicos agendados y electronica "
            "importada cotizada en dolares. El sistema desarrollado en Python resuelve ese escenario "
            "con un modelo de clases orientado a objetos, persistencia real en SQLite, validacion "
            "obligatoria de los datos del cliente, dos reglas de negocio que impiden operaciones "
            "inseguras y un precio que depende de un indicador externo obtenido desde una API publica.",
            e["cuerpo"],
        ),
        Paragraph(
            "La solucion se organiza en cuatro capas (modelo, acceso a datos, servicios e interfaz de "
            "consola) y cumple los seis requisitos minimos de la ficha del negocio exigidos por la "
            "rubrica. Adicionalmente se publico una demostracion web con una consola en vivo que "
            "ejecuta el mismo programa del repositorio.",
            e["cuerpo"],
        ),
        Paragraph("2. El problema y la solucion propuesta", e["h1"]),
        Paragraph(
            "Una tienda que vende tipos de producto con mecanicas de entrega distintas enfrenta "
            "problemas concretos: el flete solo aplica a bienes tangibles, la entrega digital no puede "
            "depender de un despacho, un servicio debe quedar agendado para una fecha futura, y el "
            "precio de la electronica importada cambia todos los dias con el dolar. Ademas, la "
            "operacion necesita controles: no se puede vender sin stock ni entregar mercaderia que no "
            "este pagada, y solo algunos roles pueden modificar el catalogo.",
            e["cuerpo"],
        ),
        Paragraph(
            "La solucion aplica los cuatro pilares de la programacion orientada a objetos. La "
            "abstraccion define el contrato de un producto; la herencia especializa ese contrato en "
            "subtipos; el polimorfismo permite que cada subtipo resuelva su propia entrega; y el "
            "encapsulamiento protege el estado interno con atributos privados y propiedades validadas.",
            e["cuerpo"],
        ),
        Paragraph("3. Arquitectura del sistema", e["h1"]),
        Paragraph(
            "El proyecto se divide en cuatro carpetas con responsabilidades separadas. Esta separacion "
            "permite cambiar la base de datos o la interfaz sin tocar las reglas del negocio.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Capa", "Carpeta", "Responsabilidad"],
            ["Modelo", "model/", "Clases del diagrama UML: cliente, productos, pedido, detalle y trabajadores."],
            ["Persistencia", "dao/", "CRUD en SQLite con consultas parametrizadas y transacciones atomicas."],
            ["Servicios", "servicios/", "Validacion de entradas, consumo de la API del dolar e inicializacion."],
            ["Interfaz", "main.py", "Menu de consola que orquesta el sistema y captura los errores."],
            ["Pruebas", "tests/", "Guion de pruebas P01 a P19 automatizado con unittest."],
        ], e), anchos=[24 * mm, 24 * mm, 118 * mm]),
        Paragraph("4. Modelo de clases orientado a objetos", e["h1"]),
        Paragraph(
            "El modelo esta compuesto por doce clases, cada una en su propio archivo dentro de la "
            "carpeta model/. Los subtipos heredan con super().__init__() y sobrescriben el metodo que "
            "varia; los atributos son privados y se acceden mediante property con validacion en el "
            "setter.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Clase", "Tipo", "Responsabilidad"],
            ["Cliente", "Entidad", "Identidad del comprador; valida RUT (Modulo 11) o correo."],
            ["Producto", "Abstracta", "Contrato del catalogo: id, nombre, precio, stock, entrega y precio final."],
            ["ProductoFisico", "Subtipo", "Despacho por transporte; calcula el flete por peso, volumen y distancia."],
            ["ProductoDigital", "Subtipo", "Entrega inmediata con enlace y licencia; flete cero."],
            ["ProductoServicio", "Subtipo", "Agenda la visita tecnica para una fecha y hora futura."],
            ["ProductoElectronica", "Subtipo", "Hereda de ProductoFisico y cotiza en USD con el dolar del dia."],
            ["DetallePedido", "Composicion", "Linea del pedido; congela cantidad y precio unitario pactado."],
            ["Pedido", "Transaccion", "Orquesta pago, despacho, totales y las dos reglas de negocio."],
            ["Trabajador", "Abstracta", "Personal, autenticacion (PBKDF2) y permisos por rol."],
            ["EncargadoBodega", "Subtipo", "Puede despachar; no puede modificar el catalogo."],
            ["Administrador", "Subtipo", "Control total del catalogo y de los precios."],
            ["Excepciones", "Apoyo", "Una excepcion propia por cada regla que impide una operacion."],
        ], e), anchos=[32 * mm, 25 * mm, 109 * mm]),
        Spacer(1, 4 * mm),
        imagen_diagrama(),
        Paragraph("Figura 1. Diagrama de clases UML del caso ClickAndGo.", e["leyenda"]),
        Paragraph("5. Persistencia de datos", e["h1"]),
        Paragraph(
            "La base de datos es SQLite y se crea automaticamente al iniciar el programa: no requiere "
            "instalacion ni scripts manuales. La capa dao/ esta completamente separada del modelo, de "
            "modo que ninguna clase del modelo contiene SQL.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Tabla", "Contenido", "Relacion"],
            ["trabajadores", "Usuarios, rol, hash PBKDF2 y salt", "-"],
            ["clientes", "Nombre e identificador validado (RUT o correo)", "1 a 0..* pedidos"],
            ["productos", "Los cuatro subtipos de producto en una sola tabla con columna tipo", "1 a * detalles"],
            ["pedidos", "Cabecera: cliente, fecha, estados y totales", "1 a 1..* detalles"],
            ["detalle_pedido", "Lineas con cantidad y precio unitario congelado", "Clave foranea a pedidos"],
            ["configuracion", "Valores de apoyo del sistema", "-"],
        ], e), anchos=[34 * mm, 92 * mm, 40 * mm]),
        Paragraph("5.1 CRUD completo", e["h2"]),
        Paragraph(
            "Las entidades principales tienen operaciones de crear, listar, obtener, actualizar y "
            "eliminar implementadas en DAO separados. El catalogo se reconstruye polimorficamente: el "
            "ProductoDAO revisa la columna tipo y devuelve la instancia de la clase correcta.",
            e["cuerpo"],
        ),
        Paragraph(
            "ProductoDAO.fila_a_producto(fila)  ->  ProductoFisico | ProductoElectronica | "
            "ProductoDigital | ProductoServicio", e["codigo"],
        ),
        Paragraph("5.2 Transaccion con lineas de detalle", e["h2"]),
        Paragraph(
            "El pedido y sus lineas se guardan dentro de una unica transaccion SQL. Si falla la "
            "insercion de cualquier linea, no queda un pedido incompleto en la base de datos.",
            e["cuerpo"],
        ),
        Paragraph(
            "with self._bd.conectar() as conexion:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;conexion.execute('INSERT INTO pedidos (...) VALUES (:id_pedido, ...)', pedido.to_dict())<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;for detalle in pedido.detalles:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conexion.execute('INSERT INTO detalle_pedido (...) VALUES (...) ', {...})<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;conexion.commit()",
            e["codigo"],
        ),
        Paragraph("5.3 Consultas parametrizadas", e["h2"]),
        Paragraph(
            "Todas las consultas usan parametros enlazados. El texto que escribe el usuario nunca se "
            "concatena dentro de una sentencia SQL, lo que neutraliza la inyeccion SQL.",
            e["cuerpo"],
        ),
        Paragraph(
            "SELECT * FROM clientes WHERE id_cliente = :id      <- correcto (parametrizado)<br/>"
            "'SELECT * FROM clientes WHERE id_cliente = ' + id   <- prohibido en este proyecto",
            e["codigo"],
        ),
        Paragraph("6. Reglas de negocio implementadas como excepciones propias", e["h1"]),
        tabla(celdas([
            ["Regla", "Excepcion", "Donde se lanza", "Efecto"],
            ["No confirmar un pedido sin stock suficiente", "StockInsuficienteError", "Pedido.confirmar_pedido()", "Impide la operacion; el stock no cambia"],
            ["No despachar un pedido impago", "PedidoNoPagadoError", "Pedido.despachar()", "Impide el despacho y mantiene el estado"],
            ["Solo el rol autorizado modifica el catalogo", "SinPermisoError", "AplicacionClickAndGo._validar_permiso_catalogo()", "El bodeguero no puede crear, modificar ni eliminar"],
            ["Dato con formato o rango invalido", "DatoInvalidoError / IdentificadorInvalidoError", "Setters del modelo y validador", "Se rechaza el dato y se vuelve a preguntar"],
            ["La API externa no responde", "IndicadorNoDisponibleError", "ServicioIndicadorDolar.obtener_valor_dolar()", "Se informa y el sistema continua"],
        ], e), anchos=[45 * mm, 38 * mm, 45 * mm, 38 * mm]),
        Paragraph(
            "Cada excepcion se captura de forma especifica en main.py. Un error de negocio muestra un "
            "mensaje al operador y devuelve el control al menu: el programa nunca se detiene por un "
            "dato invalido ni por una operacion no permitida.",
            e["cuerpo"],
        ),
        Paragraph("7. Validacion de entradas", e["h1"]),
        Paragraph(
            "Todas las entradas del usuario se validan antes de usarse, considerando tipo, formato y "
            "rango. Si el dato es invalido, se informa el problema y se solicita nuevamente.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Dato", "Validacion aplicada", "Caso de prueba"],
            ["RUT del cliente", "Algoritmo Modulo 11 sobre el cuerpo y digito verificador", "P07 / P08"],
            ["Correo del cliente", "Expresion regular de formato sintactico", "P07 / P08"],
            ["Cantidad de una linea", "Entero mayor que cero", "P19"],
            ["Precio y stock", "Decimal no negativo / entero no negativo", "P19"],
            ["Fecha del servicio", "Formato AAAA-MM-DD HH:MM y fecha futura", "P11"],
            ["Enlace de descarga", "Debe comenzar con http:// o https://", "P10"],
            ["Opcion de menu", "Debe existir entre las opciones validas", "P18"],
        ], e), anchos=[40 * mm, 90 * mm, 36 * mm]),
        Paragraph(
            "El dato obligatorio que exige la ficha (RUT o correo) se valida dentro del setter del "
            "modelo, de modo que la proteccion no depende de la interfaz: aunque otro programa use "
            "estas clases, el objeto con un identificador invalido no puede existir.",
            e["cuerpo"],
        ),
        Paragraph("8. Consumo de un servicio externo", e["h1"]),
        Paragraph(
            "El precio de la electronica importada se obtiene multiplicando su valor en dolares por el "
            "valor del dolar observado del dia. Ese indicador se consulta a la API publica "
            "mindicador.cl mediante la libreria oficial requests, con un tiempo maximo de espera de "
            "cinco segundos.",
            e["cuerpo"],
        ),
        Paragraph(
            "respuesta = requests.get(self._url, timeout=self._timeout)<br/>"
            "respuesta.raise_for_status()<br/>"
            "serie = respuesta.json().get('serie') or []<br/>"
            "ultimo = serie[0]<br/>"
            "return ValorDolar(float(ultimo['valor']), str(ultimo['fecha'])[:10], 'mindicador.cl')",
            e["codigo"],
        ),
        Paragraph(
            "Si la API no responde, el servicio lanza IndicadorNoDisponibleError y guarda el ultimo "
            "valor conocido en datos/dolar_respaldo.json. En la siguiente consulta sin conexion el "
            "programa utiliza ese respaldo, informa que no pudo obtener el valor del dia y continua "
            "funcionando: es exactamente lo que exige el caso P17 del guion de pruebas.",
            e["cuerpo"],
        ),
        Paragraph("9. Decisiones de seguridad", e["h1"]),
        Paragraph("9.1 Autenticacion de trabajadores", e["h2"]),
        Paragraph(
            "Las contrasenas no se guardan en texto plano. Cada trabajador tiene un salt aleatorio de "
            "16 bytes y su contrasena se almacena como PBKDF2-HMAC-SHA256 con 120.000 iteraciones. La "
            "comparacion se realiza con hmac.compare_digest, que evita filtrar informacion por el "
            "tiempo de respuesta.",
            e["cuerpo"],
        ),
        Paragraph("9.2 Control de acceso basado en roles (RBAC)", e["h2"]),
        Paragraph(
            "El permiso no se resuelve con una condicion sobre un texto, sino con el metodo "
            "polimorfico de cada trabajador. El EncargadoBodega puede despachar pero no modificar el "
            "catalogo; el Administrador puede hacer ambas cosas. Cuando la accion no esta autorizada "
            "se lanza SinPermisoError.",
            e["cuerpo"],
        ),
        Paragraph("9.3 Inyeccion SQL", e["h2"]),
        Paragraph(
            "Todas las sentencias son parametrizadas y la conexion activa PRAGMA foreign_keys = ON "
            "para resguardar la integridad referencial. La combinacion de parametros enlazados y "
            "validacion previa de tipos cierra las dos vias clasicas de ataque sobre una base de datos.",
            e["cuerpo"],
        ),
        Paragraph("10. Uso de herramientas de IA", e["h1"]),
        Paragraph(
            "La asignatura permite usar asistentes de inteligencia artificial, exigiendo documentar "
            "que se adopto, que se modifico y que se descarto, con su razon tecnica.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Sugerencia de la IA", "Decision", "Razon tecnica"],
            ["Usar sqlite3.Row y acceder a las columnas por nombre en lugar de por indice numerico.", "Adoptada",
             "El codigo queda autoexplicativo y un cambio en el orden del SELECT no rompe la construccion de objetos."],
            ["Consumir la API del dolar con requests.get(URL) sin tiempo maximo de espera.", "Modificada",
             "Se agrego timeout=5 y captura especifica de fallas de red y de respuesta, porque el criterio 3.1.3 exige continuidad del sistema."],
            ["Resolver el tipo de producto con una cadena if/elif dentro de Pedido.", "Descartada",
             "La rubrica indica que reemplazar el polimorfismo por if sobre el tipo corresponde al nivel En desarrollo."],
            ["Guardar la contrasena con hashlib.md5.", "Descartada",
             "MD5 no es apto para contrasenas; se uso PBKDF2-HMAC-SHA256 con salt aleatorio."],
            ["Capturar los errores de la API con 'except Exception: pass'.", "Descartada",
             "Ocultar el error impide informar al usuario; se capturan excepciones concretas y se informa."],
        ], e), anchos=[58 * mm, 22 * mm, 86 * mm]),
        Paragraph("11. Guion de pruebas y resultados", e["h1"]),
        Paragraph(
            "Los 19 casos del guion de pruebas entregado se ejecutan de forma automatizada con el "
            "comando python tests/test_guion_pruebas.py. Todos los casos finalizaron satisfactoriamente.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["N", "Que se prueba", "Resultado esperado", "Estado"],
            ["P01", "El programa se ejecuta y muestra el menu", "El programa inicia y muestra el menu", "Cumple"],
            ["P02", "Crear producto", "El programa confirma que se guardo", "Cumple"],
            ["P03", "Listar producto", "Aparece el registro recien creado", "Cumple"],
            ["P04", "Modificar producto", "El listado muestra el cambio de stock", "Cumple"],
            ["P05", "Persistencia al reiniciar", "El registro sigue guardado", "Cumple"],
            ["P06", "Eliminar producto", "El registro ya no aparece", "Cumple"],
            ["P07", "Correo o RUT correcto", "Lo acepta", "Cumple"],
            ["P08", "Correo incompleto", "Lo rechaza con mensaje y continua", "Cumple"],
            ["P09", "Producto fisico", "Despacha por transporte y calcula flete", "Cumple"],
            ["P10", "Producto digital", "Entrega instantanea con link, sin despacho", "Cumple"],
            ["P11", "Servicio", "Se agenda para una fecha futura", "Cumple"],
            ["P12", "Pedido multi-linea", "Queda guardado como un solo registro", "Cumple"],
            ["P13", "Detalle del pedido", "Se ven todas sus lineas de detalle", "Cumple"],
            ["P14", "Confirmar sin stock", "Se impide; el stock no cambia", "Cumple"],
            ["P15", "Despachar un pedido impago", "La operacion se impide", "Cumple"],
            ["P16", "Dolar del dia", "Usa el valor del dolar de hoy", "Cumple"],
            ["P17", "Sin internet", "Avisa y no se cae", "Cumple"],
            ["P18", "Opcion de menu inexistente", "Muestra mensaje y vuelve al menu", "Cumple"],
            ["P19", "Letras en un campo numerico", "Muestra mensaje y no se cae", "Cumple"],
        ], e), anchos=[12 * mm, 58 * mm, 72 * mm, 24 * mm]),
        Paragraph("12. Matriz de cumplimiento de la rubrica", e["h1"]),
        tabla(celdas([
            ["Criterio", "Exigencia", "Evidencia en el proyecto", "Nivel"],
            ["2.1.2 Modelo orientado a objetos", "Clases coherentes con el diagrama, herencia con super() y polimorfismo, atributos privados con property y validacion.",
             "model/ con doce clases, herencia de Producto y Trabajador, propiedades validadas y procesar_entrega() sobrescrito.", "Destacado"],
            ["2.1.3 Librerias oficiales para base de datos", "CRUD completo mediante DAO, transaccion con lineas, consultas parametrizadas y tablas creadas al iniciar.",
             "dao/ con cuatro DAO, insercion atomica de pedido y detalles, sentencias con parametros y esquema automatico.", "Destacado"],
            ["2.1.4 Manejo de errores con excepciones propias", "Una excepcion propia por cada regla, lanzada y capturada con try/except especifico.",
             "StockInsuficienteError y PedidoNoPagadoError (mas SinPermisoError y otras) capturadas en main.py sin detener el programa.", "Destacado"],
            ["3.1.2 Validacion de entradas", "Todas las entradas se validan antes de usarse (tipo, formato y rango).",
             "Setters del modelo y servicios/validador.py con reintento; el dato de la ficha se valida en el setter.", "Destacado"],
            ["3.1.1 / 3.1.3 API externa y continuidad", "Precio con indicador obtenido con requests, tiempo maximo de espera y continuidad ante fallas.",
             "ServicioIndicadorDolar con timeout=5, respaldo local y aviso al usuario sin detener el sistema.", "Destacado"],
            ["3.1.4 Seguridad del codigo con apoyo de IA", "README que permita instalar y ejecutar, explique decisiones de seguridad y ejemplos concretos de uso de IA.",
             "README con instalacion, decisiones de seguridad y tres casos concretos (adoptado, modificado, descartado).", "Destacado"],
        ], e), anchos=[40 * mm, 52 * mm, 58 * mm, 16 * mm]),
        Paragraph("13. Conclusiones", e["h1"]),
        Paragraph(
            "El sistema ClickAndGo cumple los seis requisitos minimos de la ficha del negocio y los "
            "seis criterios de la rubrica de la Evaluacion Sumativa N2. La separacion entre modelo, "
            "persistencia y servicios permite que las reglas del negocio esten protegidas de forma "
            "independiente de la interfaz: el modelo rechaza datos invalidos por si mismo, el DAO "
            "impide la inyeccion SQL y la capa de servicios aísla la dependencia de la API externa.",
            e["cuerpo"],
        ),
        Paragraph(
            "El uso de excepciones propias para cada regla transforma los controles del negocio en "
            "parte del diseno del software, y no en simples mensajes en pantalla. Ese es el aporte "
            "central del proyecto: un sistema que no se cae cuando el usuario se equivoca ni cuando un "
            "servicio externo falla.",
            e["cuerpo"],
        ),
    ]

    documento.build(contenido)


# ----------------------------------------------------------------------
# Documento 2: guia del cliente desde cero
# ----------------------------------------------------------------------
def build_guia(ruta_salida: Path) -> None:
    estilos = crear_estilos()
    documento = DocumentoClickAndGo(
        str(ruta_salida), "Guia del cliente - Proyecto y codigo (ClickAndGo)"
    )
    e = estilos
    contenido: list = []

    contenido += cubierta(
        e,
        "Guia para conocer el proyecto desde cero",
        "Que es ClickAndGo, como se usa y como esta construido su codigo<br/>Documento de presentacion para el cliente",
        [
            ("Proyecto", "ClickAndGo - Tienda de comercio electronico"),
            ("Preparado por", "Miguel Troncoso y Alexandy Remicinthe"),
            ("Asignatura", "Programacion Orientada a Objeto Seguro - TI3V21"),
            ("Institucion", "INACAP - Sede Puente Alto"),
            ("Fecha", "Octubre de 2026"),
            ("Repositorio del codigo", "https://github.com/MiguelTroncoso/ecommerce"),
            ("Demostracion en linea", "https://inacap.superflash.site"),
        ],
    )

    contenido += [
        Paragraph("1. Que es ClickAndGo, en palabras simples", e["h1"]),
        Paragraph(
            "ClickAndGo es una tienda que vende cosas muy distintas entre si: productos que se despachan "
            "fisicamente a la casa del cliente, productos que se entregan por internet al instante, "
            "servicios que un tecnico realiza en terreno y productos importados cuyo precio cambia "
            "todos los dias porque se paga en dolares.",
            e["cuerpo"],
        ),
        Paragraph(
            "El sistema que construimos es el programa que administra esa tienda: registra clientes, "
            "mantiene el catalogo, arma los pedidos, calcula los totales, controla el stock, impide las "
            "operaciones riesgosas y deja todo guardado para que la informacion no se pierda cuando se "
            "cierra el programa.",
            e["cuerpo"],
        ),
        Paragraph("2. Que puede hacer el sistema", e["h1"]),
        tabla(celdas([
            ["Funcion", "Que permite hacer"],
            ["Gestionar clientes", "Registrar, listar, modificar y eliminar clientes validando su RUT o su correo."],
            ["Gestionar catalogo", "Crear, listar, modificar y eliminar productos de los cuatro tipos."],
            ["Gestionar pedidos", "Armar un pedido con varias lineas, ver su detalle, confirmarlo, registrar el pago y despacharlo."],
            ["Calcular precios", "Convertir el precio de la electronica importada usando el dolar del dia."],
            ["Controlar permisos", "Cada trabajador tiene un rol con permisos distintos."],
            ["Mantener los datos", "Todo queda guardado en una base de datos SQLite local."],
        ], e), anchos=[42 * mm, 124 * mm]),
        Paragraph("3. Los cuatro tipos de producto", e["h1"]),
        Paragraph("3.1 Producto fisico", e["h2"]),
        Paragraph(
            "Es un bien tangible: una silla, un teclado, un monitor. Cuando se vende, el sistema genera "
            "una orden de despacho por transporte y calcula el flete considerando el peso, el volumen y "
            "la distancia de entrega. El flete se suma al total del pedido.",
            e["cuerpo"],
        ),
        Paragraph("3.2 Producto digital", e["h2"]),
        Paragraph(
            "Es un bien que no se despacha: una licencia de software, un antivirus, un libro "
            "electronico. La entrega es inmediata: el sistema muestra el enlace de descarga y la "
            "licencia de activacion. El costo de despacho es cero.",
            e["cuerpo"],
        ),
        Paragraph("3.3 Servicio", e["h2"]),
        Paragraph(
            "Es un trabajo que se realiza en terreno, como instalar una red domiciliaria. El sistema "
            "exige una fecha y hora futura, registra la direccion de la visita y la duracion estimada. "
            "No existe despacho de carga.",
            e["cuerpo"],
        ),
        Paragraph("3.4 Electronica importada", e["h2"]),
        Paragraph(
            "Es un producto fisico que se compra en dolares. Su precio en pesos no esta fijo en el "
            "catalogo: se calcula en el momento multiplicando el valor en dolares por el valor del "
            "dolar observado del dia, que el sistema consulta en una pagina publica del gobierno "
            "(mindicador.cl).",
            e["cuerpo"],
        ),
        Paragraph(
            "Ejemplo: si un monitor cuesta USD 250 y el dolar del dia es de $977,25, el sistema calcula "
            "un precio de $244.312 pesos y lo usa en el pedido.",
            e["nota"],
        ),
        Paragraph("4. Como se usa el sistema, paso a paso", e["h1"]),
        Paragraph(
            "El programa se maneja con un menu numerado. Estas son las seis acciones mas importantes y "
            "lo que ocurre en cada una.",
            e["cuerpo"],
        ),
        Paragraph("Paso 1. Registrar un cliente", e["h3"]),
        Paragraph(
            "Se elige la opcion 1 (Clientes) y luego la opcion 1 (Crear cliente). El sistema pide el "
            "nombre y el identificador. Si se elige RUT, lo valida con el algoritmo Modulo 11 chileno; "
            "si se elige correo, valida que tenga el formato correcto. Si el dato esta mal escrito, el "
            "sistema lo rechaza con un mensaje y vuelve a preguntar: nunca guarda un cliente invalido.",
            e["cuerpo"],
        ),
        Paragraph("Paso 2. Cargar productos al catalogo", e["h3"]),
        Paragraph(
            "Se elige la opcion 2 (Productos) y luego Crear producto. El sistema pregunta de que tipo "
            "es (fisico, digital, servicio o importado) y pide los datos que corresponden a ese tipo. "
            "Por ejemplo, para un producto digital solicita el enlace de descarga y la licencia; para "
            "un servicio, la fecha de la visita.",
            e["cuerpo"],
        ),
        Paragraph("Paso 3. Crear un pedido", e["h3"]),
        Paragraph(
            "Se elige la opcion 3 (Pedidos) y luego Crear pedido. El sistema pide el cliente y luego "
            "va agregando lineas: producto y cantidad, una por una. Se termina escribiendo FIN. En "
            "cualquier momento se puede ver el total, que incluye los productos mas los fletes de los "
            "bienes fisicos.",
            e["cuerpo"],
        ),
        Paragraph("Paso 4. Confirmar el pedido", e["h3"]),
        Paragraph(
            "Confirmar significa que el sistema revisa que exista stock suficiente para todas las "
            "lineas. Si falta stock, la confirmacion se bloquea con un mensaje claro y el inventario "
            "queda intacto. Es la primera regla del negocio.",
            e["cuerpo"],
        ),
        Paragraph("Paso 5. Registrar el pago y despachar", e["h3"]),
        Paragraph(
            "Al registrar el pago, el sistema descuenta el stock y marca el pedido como PAGADO. "
            "Recien entonces se permite despacharlo. Si alguien intenta despachar un pedido que aun no "
            "esta pagado, el sistema lo impide: es la segunda regla del negocio.",
            e["cuerpo"],
        ),
        Paragraph("Paso 6. Ver las entregas", e["h3"]),
        Paragraph(
            "La opcion Procesar entrega muestra, linea por linea, como se entrega cada producto. Es la "
            "parte mas importante del diseno: el sistema no pregunta de que tipo es el producto, cada "
            "producto sabe como se entrega.",
            e["cuerpo"],
        ),
        Paragraph("5. Quien puede hacer que cosa", e["h1"]),
        tabla(celdas([
            ["Accion", "Administrador", "Encargado de bodega"],
            ["Crear, modificar o eliminar productos", "Si", "No (el sistema lo impide)"],
            ["Cambiar precios", "Si", "No"],
            ["Registrar pagos", "Si", "Si"],
            ["Despachar pedidos", "Si", "Si"],
            ["Consultar el catalogo y los pedidos", "Si", "Si"],
        ], e), anchos=[80 * mm, 40 * mm, 46 * mm]),
        Paragraph(
            "Las contrasenas no se guardan como texto: se guardan cifradas con un algoritmo de "
            "derivacion (PBKDF2) y una clave distinta por usuario. Aunque alguien vea el archivo de la "
            "base de datos, no puede leer las contrasenas.",
            e["nota"],
        ),
        Paragraph("6. Donde queda guardada la informacion", e["h1"]),
        Paragraph(
            "El sistema usa una base de datos SQLite llamada clickandgo.db dentro de la carpeta datos/. "
            "Esa base se crea sola la primera vez que se ejecuta el programa y guarda clientes, "
            "productos, pedidos, lineas de detalle y trabajadores. Gracias a eso, al cerrar y volver a "
            "abrir el programa la informacion sigue estando.",
            e["cuerpo"],
        ),
        Paragraph("7. Como esta construido el sistema", e["h1"]),
        Paragraph(
            "El codigo esta separado en cuatro partes. Pensemos en una tienda real: el modelo son los "
            "conceptos del negocio (producto, pedido, cliente); el DAO es el bodeguero que guarda y "
            "recupera las cosas del almacen; los servicios son los tramites externos (validar un RUT, "
            "consultar el dolar); y main.py es el mostrador donde el usuario hace sus pedidos.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Carpeta", "En palabras simples", "Ejemplos de archivos"],
            ["model/", "Los conceptos del negocio y sus reglas.", "cliente.py, producto.py, pedido.py"],
            ["dao/", "Quien guarda y recupera la informacion.", "conexion.py, producto_dao.py, pedido_dao.py"],
            ["servicios/", "Los tramites externos y la validacion.", "validador.py, indicador_dolar.py"],
            ["main.py", "El menu que usa la persona.", "menu principal y submenus"],
        ], e), anchos=[26 * mm, 66 * mm, 74 * mm]),
        Paragraph("8. Recorrido del codigo, archivo por archivo", e["h1"]),
        Paragraph(
            "Esta seccion es para quien quiera leer el codigo. Se recomienda revisarlo en este orden.",
            e["cuerpo"],
        ),
        Paragraph("8.1 model/cliente.py", e["h2"]),
        Paragraph(
            "Define al comprador. Su dato mas importante es el identificador, que se valida al "
            "asignarlo. Si el RUT no cumple el Modulo 11 o el correo no tiene formato valido, el "
            "sistema lanza un error y el cliente no se crea.",
            e["cuerpo"],
        ),
        Paragraph(
            "@identificador.setter<br/>"
            "def identificador(self, valor):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;if self._tipo_identificador == 'EMAIL':<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not validar_email(valor):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise IdentificadorInvalidoError(...)",
            e["codigo"],
        ),
        Paragraph("8.2 model/producto.py y sus subtipos", e["h2"]),
        Paragraph(
            "producto.py define el contrato comun: identificador, nombre, precio, stock y los dos "
            "metodos que cambian segun el tipo (procesar_entrega y calcular_precio_final). Los otros "
            "cuatro archivos son los subtipos, que heredan de Producto con super().__init__() y "
            "sobrescriben el metodo de entrega.",
            e["cuerpo"],
        ),
        tabla(celdas([
            ["Archivo", "Que agrega"],
            ["producto_fisico.py", "Peso, volumen y tarifa de flete; calcula el flete y genera la orden de transporte."],
            ["producto_digital.py", "Enlace de descarga, licencia y peso del archivo; entrega instantanea sin flete."],
            ["producto_servicio.py", "Fecha agendada, direccion y duracion; valida que la fecha sea futura."],
            ["producto_electronica.py", "Precio en USD y garantia; convierte a pesos con el dolar del dia."],
        ], e), anchos=[40 * mm, 126 * mm]),
        Paragraph("8.3 model/pedido.py", e["h2"]),
        Paragraph(
            "Es la clase mas importante del negocio. Arma el pedido agregando lineas, calcula el total "
            "con los fletes, confirma el pedido verificando el stock, registra el pago descontando el "
            "inventario y autoriza el despacho. Aqui viven las dos reglas que impiden una operacion.",
            e["cuerpo"],
        ),
        Paragraph(
            "def confirmar_pedido(self):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;for detalle in self._detalles:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not detalle.producto.tiene_stock_suficiente(detalle.cantidad):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise StockInsuficienteError(...)<br/><br/>"
            "def despachar(self, operador):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;if self._estado_pago != 'PAGADO':<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise PedidoNoPagadoError(self._id_pedido, self._estado_pago)",
            e["codigo"],
        ),
        Paragraph("8.4 dao/conexion.py", e["h2"]),
        Paragraph(
            "Crea el archivo de la base de datos, activa las claves foraneas y ejecuta el esquema "
            "completo de tablas cuando el programa inicia. Tambien contiene los metodos que ejecutan "
            "las consultas con parametros.",
            e["cuerpo"],
        ),
        Paragraph("8.5 dao/pedido_dao.py", e["h2"]),
        Paragraph(
            "Guarda el pedido completo. Primero registra la cabecera y despues cada una de sus lineas "
            "de detalle, todo dentro de la misma transaccion para que la informacion nunca quede a "
            "medias.",
            e["cuerpo"],
        ),
        Paragraph("8.6 servicios/indicador_dolar.py", e["h2"]),
        Paragraph(
            "Consulta el valor del dolar en la pagina del gobierno y guarda una copia del ultimo valor "
            "conocido. Si no hay internet, entrega el valor guardado y un aviso, para que la tienda "
            "pueda seguir cotizando.",
            e["cuerpo"],
        ),
        Paragraph("8.7 main.py", e["h2"]),
        Paragraph(
            "Es la puerta de entrada al sistema: muestra el menu, pide los datos, los valida y llama a "
            "las clases del modelo y del DAO. Tambien captura los errores de negocio para mostrar un "
            "mensaje claro sin que el programa se detenga.",
            e["cuerpo"],
        ),
        Paragraph("9. Preguntas frecuentes", e["h1"]),
        Paragraph("Que pasa si me equivoco al escribir la cantidad?", e["h3"]),
        Paragraph(
            "El sistema muestra un mensaje indicando que el valor no es un numero valido y vuelve a "
            "pedirlo. El programa no se cierra y no guarda informacion incorrecta.",
            e["cuerpo"],
        ),
        Paragraph("Que pasa si internet se corta cuando se calcula el precio del dolar?", e["h3"]),
        Paragraph(
            "El sistema avisa que no pudo obtener el valor del dia y utiliza el ultimo valor que "
            "conoce, o informa que no puede cotizar. En ningun caso el programa se cae ni se pierde la "
            "informacion ya guardada.",
            e["cuerpo"],
        ),
        Paragraph("Puedo vender mas unidades de las que tengo?", e["h3"]),
        Paragraph(
            "No. La confirmacion del pedido verifica el stock de todas las lineas. Si falta stock, la "
            "operacion se bloquea y el inventario no cambia.",
            e["cuerpo"],
        ),
        Paragraph("Puedo despachar un pedido que el cliente no ha pagado?", e["h3"]),
        Paragraph(
            "No. El sistema lo impide y explica el motivo. Solo se despachan pedidos con estado "
            "PAGADO, y solo con un trabajador autorizado.",
            e["cuerpo"],
        ),
        Paragraph("Se pierde la informacion al cerrar el programa?", e["h3"]),
        Paragraph(
            "No. Todo se guarda en la base de datos datos/clickandgo.db y sigue disponible la proxima "
            "vez que se abra el programa.",
            e["cuerpo"],
        ),
        Paragraph("10. Como instalar y ejecutar el sistema", e["h1"]),
        Paragraph(
            "Se necesita Python 3.11 o superior. En una terminal se ejecutan estos comandos:",
            e["cuerpo"],
        ),
        Paragraph(
            "git clone https://github.com/MiguelTroncoso/ecommerce.git<br/>"
            "cd ecommerce<br/>"
            "python -m venv .venv<br/>"
            "source .venv/bin/activate&nbsp;&nbsp;&nbsp;&nbsp; (en Windows: .venv\\Scripts\\activate)<br/>"
            "pip install -r requirements.txt<br/>"
            "python main.py",
            e["codigo"],
        ),
        Paragraph(
            "Tambien se puede ver el sistema funcionando en linea, sin instalar nada, en "
            "https://inacap.superflash.site, donde existe una consola en vivo que ejecuta exactamente "
            "el mismo programa del repositorio.",
            e["cuerpo"],
        ),
        Paragraph("11. Glosario breve", e["h1"]),
        tabla(celdas([
            ["Termino", "Significado"],
            ["Programacion orientada a objetos (POO)", "Forma de programar organizando el software en clases que representan conceptos del negocio."],
            ["Clase y objeto", "La clase es el molde (Producto) y el objeto es cada cosa concreta creada con ese molde (una silla)."],
            ["Herencia", "Un tipo de producto puede reutilizar el comportamiento de otro mas general y especializarlo."],
            ["Polimorfismo", "Cada tipo de producto responde a la misma orden de entrega a su propia manera."],
            ["Encapsulamiento", "Los datos internos se protegen y solo se modifican con reglas de validacion."],
            ["Base de datos SQLite", "Archivo unico donde se guarda la informacion de forma permanente."],
            ["API", "Servicio de internet que entrega datos; en este caso, el valor del dolar del dia."],
            ["Excepcion", "Aviso formal de que una operacion no se puede realizar; el sistema lo captura y explica el motivo."],
            ["DAO", "Capa del programa que se encarga exclusivamente de guardar y leer datos."],
        ], e), anchos=[52 * mm, 114 * mm]),
    ]

    documento.build(contenido)


def main() -> None:
    informe = DIR_DOCS / "ES2_114-2A-F2_ecommerce.pdf"
    guia = DIR_DOCS / "GUIA_CLIENTE_ClickAndGo.pdf"
    build_informe(informe)
    build_guia(guia)
    print(f"Generado: {informe}")
    print(f"Generado: {guia}")


if __name__ == "__main__":
    main()
