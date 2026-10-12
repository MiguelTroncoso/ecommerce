#!/usr/bin/env python3
"""Genera el guion de la defensa oral de la Evaluacion Sumativa N3.

Contenido:

1. Datos de la presentacion y checklist previo.
2. Reparto de la presentacion entre los dos integrantes.
3. Guion minuto a minuto con el texto que dice cada uno.
4. Frases de transicion.
5. Banco de preguntas del docente con la respuesta preparada.
6. Fichas rapidas por archivo y el efecto de cada cambio posible.
7. Errores a evitar y cierre.

Uso:

    python docs/build_guion_defensa.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

DIR_DOCS = Path(__file__).resolve().parent
SALIDA = DIR_DOCS / "ES3_114-2A-F2_guion_defensa.pdf"

AZUL = colors.HexColor("#0D233A")
AZUL_CLARO = colors.HexColor("#1C4E80")
ROJO = colors.HexColor("#D63426")
GRIS = colors.HexColor("#F2F5F9")
BORDE = colors.HexColor("#D6DEE8")
TEXTO = colors.HexColor("#1F2933")


class DocumentoGuion(BaseDocTemplate):
    def __init__(self, ruta: str) -> None:
        super().__init__(
            ruta,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=16 * mm,
            title="Guion de la defensa oral - ClickAndGo (ES3)",
            author="Miguel Troncoso y Alexandy Remicinthe",
            subject="INACAP TI3V21 - Evaluacion Sumativa N3",
        )
        marco = Frame(18 * mm, 16 * mm, A4[0] - 36 * mm, A4[1] - 36 * mm, id="normal")
        self.addPageTemplates([PageTemplate(id="principal", frames=[marco], onPage=self._decorar)])

    def _decorar(self, lienzo: canvas.Canvas, documento) -> None:
        if documento.page == 1:
            return
        lienzo.saveState()
        lienzo.setStrokeColor(BORDE)
        lienzo.setLineWidth(0.6)
        lienzo.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
        lienzo.setFont("Helvetica", 8)
        lienzo.setFillColor(colors.HexColor("#667788"))
        lienzo.drawString(18 * mm, A4[1] - 12 * mm,
                          "Guion de la defensa oral - ClickAndGo (grupo 05, E-commerce)")
        lienzo.drawRightString(A4[0] - 18 * mm, A4[1] - 12 * mm, "INACAP TI3V21")
        lienzo.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        lienzo.drawString(18 * mm, 9 * mm,
                          "Evaluacion Sumativa N3 - martes 13 de octubre de 2026, 21:30 hrs - A403")
        lienzo.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Pagina {documento.page}")
        lienzo.restoreState()


def crear_estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "cubierta_titulo": ParagraphStyle(
            "cubierta_titulo", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=27, leading=32, textColor=AZUL, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cubierta_sub": ParagraphStyle(
            "cubierta_sub", parent=base["Normal"], fontName="Helvetica", fontSize=12.5,
            leading=18, textColor=AZUL_CLARO, alignment=TA_CENTER, spaceAfter=3,
        ),
        "cubierta_doc": ParagraphStyle(
            "cubierta_doc", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=15,
            leading=20, textColor=ROJO, alignment=TA_CENTER,
        ),
        "cubierta_dato": ParagraphStyle(
            "cubierta_dato", parent=base["Normal"], fontName="Helvetica", fontSize=10,
            leading=15, textColor=TEXTO,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15,
            leading=19, textColor=AZUL, spaceBefore=14, spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.8,
            leading=15, textColor=AZUL_CLARO, spaceBefore=11, spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.4,
            leading=13, textColor=AZUL, spaceBefore=8, spaceAfter=3,
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo", parent=base["BodyText"], fontName="Helvetica", fontSize=9.7,
            leading=14, textColor=TEXTO, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "vineta": ParagraphStyle(
            "vineta", parent=base["BodyText"], fontName="Helvetica", fontSize=9.7,
            leading=13.8, textColor=TEXTO, leftIndent=11, bulletIndent=2, spaceAfter=3,
        ),
        "guion": ParagraphStyle(
            "guion", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=9.8,
            leading=14.4, textColor=colors.HexColor("#123B5E"), alignment=TA_JUSTIFY,
            backColor=colors.HexColor("#EEF4FA"), borderPadding=8, leftIndent=4,
            rightIndent=4, spaceBefore=3, spaceAfter=8,
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName="Courier", fontSize=8.1,
            leading=11, textColor=AZUL, backColor=colors.HexColor("#F4F7FB"),
            borderPadding=6, leftIndent=4, rightIndent=4, spaceBefore=3, spaceAfter=7,
        ),
        "celda": ParagraphStyle(
            "celda", parent=base["Normal"], fontName="Helvetica", fontSize=8.2,
            leading=11.2, textColor=TEXTO,
        ),
        "celda_encabezado": ParagraphStyle(
            "celda_encabezado", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.4, leading=11.4, textColor=colors.white,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=9.2,
            leading=13, textColor=colors.HexColor("#5A4A00"),
            backColor=colors.HexColor("#FFF8E6"), borderPadding=7,
            alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=8,
        ),
    }


def tabla(filas: list[list[str]], estilos: dict, anchos: list[float]) -> Table:
    datos = []
    for indice, fila in enumerate(filas):
        estilo = estilos["celda_encabezado"] if indice == 0 else estilos["celda"]
        datos.append([Paragraph(str(celda), estilo) for celda in fila])
    tabla_ = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    tabla_.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabla_


PREGUNTAS = [
    ["Que pasaria si la consulta se armara concatenando texto en vez de usar parametros?",
     "Se abre la puerta a la inyeccion SQL: si el usuario escribe comillas o un punto y coma, ese texto pasaria a formar parte de la sentencia y podria alterar o borrar datos. Con parametros enlazados el valor viaja como dato, nunca como instruccion. Se muestra en dao/conexion.py."],
    ["Que pasaria si se quita la validacion del RUT?",
     "El setter aceptaria cualquier texto como identificador, se guardaria un cliente invalido y la regla de la ficha dejaria de cumplirse. La validacion esta en el setter, no en el menu, para que la proteccion no dependa de la interfaz."],
    ["Por que usaron excepciones propias y no un return False?",
     "Porque una excepcion obliga a quien llama a manejarla y permite distinguir el motivo. Ademas la rubrica pide una excepcion propia por cada regla. Se capturan en main.py y el programa informa y continua."],
    ["Donde se descuenta el stock y por que en ese lugar?",
     "En Pedido.registrar_pago(), despues de confirmar que hay stock, y en Producto.descontar_stock(). Si se descontara antes de confirmar, un pedido rechazado habria bajado el inventario igual."],
    ["Que pasa si la API del dolar no responde?",
     "La consulta tiene timeout de cinco segundos y lanza IndicadorNoDisponibleError. valor_para_calculo() usa el ultimo valor guardado en datos/dolar_respaldo.json y avisa al operador. El sistema sigue funcionando: es el caso P17."],
    ["Por que el precio de la electronica no se guarda en pesos en el catalogo?",
     "Porque depende del dolar del dia. Se guarda el costo en USD y se convierte al vender. El precio convertido queda congelado en la linea de detalle, para que el pedido no cambie si el dolar sube despues."],
    ["Que diferencia hay entre composicion y agregacion en su modelo?",
     "Pedido y DetallePedido es composicion: la linea no existe sin el pedido y se elimina con el, declarado con ON DELETE CASCADE. DetallePedido y Producto es agregacion: si se elimina la linea o el pedido, el producto sigue en el catalogo."],
    ["Como evitan que dos productos tengan el mismo codigo?",
     "GeneradorCodigos calcula el mayor numero usado y verifica con una consulta si el codigo candidato ya existe; si existe, prueba el siguiente. Por eso el codigo no se escribe a mano."],
    ["Que hace PRAGMA foreign_keys = ON?",
     "Activa la revision de claves foraneas en SQLite. Sin eso se podria guardar un pedido con un cliente inexistente o una linea con un producto que no existe."],
    ["Que pasa si se elimina un pedido?",
     "Se elimina la cabecera y, por la clausula ON DELETE CASCADE, tambien sus lineas de detalle. El producto sigue intacto porque es una agregacion."],
    ["Como se guardan las contrasenas?",
     "Con PBKDF2-HMAC-SHA256, 120.000 iteraciones y una sal aleatoria de 16 bytes por usuario. La comparacion usa hmac.compare_digest. Nunca se guarda la contrasena en texto plano."],
    ["Que es un DAO y por que lo separaron del modelo?",
     "Es la capa que guarda y lee datos. Se separa para que las clases del modelo no contengan SQL: asi se puede cambiar la base de datos sin tocar las reglas del negocio."],
    ["Que parte del codigo propuso la IA y que hicieron con eso?",
     "Esta en el README, seccion de uso de IA. Adoptamos el acceso por nombre de columna con sqlite3.Row; modificamos la consulta a la API agregando timeout y captura de errores; descartamos el if en vez de polimorfismo y el hash MD5."],
    ["Que pasaria si se elimina el timeout de la consulta a la API?",
     "Si el servidor no responde, el programa quedaria esperando indefinidamente y el usuario no podria seguir. El timeout garantiza la continuidad del sistema, que es un criterio de la rubrica."],
    ["Por que reintentan en la validacion en vez de mostrar un mensaje y salir?",
     "Porque la rubrica exige que un dato invalido se rechace con un mensaje sin detener el programa. El reintento permite corregir el dato y continuar la operacion."],
    ["Que cambiarian si tuvieran mas tiempo?",
     "Agregar pruebas unitarias por clase, separar las credenciales en un archivo de configuracion y agregar un registro de auditoria de las operaciones criticas."],
]

FICHAS = [
    ["dao/conexion.py",
     "Define el esquema de las seis tablas, crea la base de datos al iniciar y ejecuta todas las consultas con parametros. El envoltorio de conexion cierra siempre el archivo para no dejar descriptores abiertos.",
     "Si se quita PRAGMA foreign_keys, se pueden guardar pedidos con clientes inexistentes. Si una consulta se arma con concatenacion en vez de parametros, se abre la inyeccion SQL."],
    ["dao/producto_dao.py",
     "Guarda los cuatro tipos de producto en una sola tabla con una columna tipo. Al leer, fila_a_producto() revisa el tipo y construye la instancia de la clase correcta.",
     "Si se agrega un tipo de producto nuevo, hay que agregar su caso en fila_a_producto y su valor permitido en el esquema; si no, la lectura falla."],
    ["dao/pedido_dao.py",
     "Guarda la cabecera del pedido y despues cada linea de detalle dentro de la misma conexion, con un solo commit. Ademas reconstruye el pedido con sus lineas al leerlo.",
     "Si el commit quedara dentro del ciclo de las lineas, un error a mitad de camino dejaria un pedido sin todas sus lineas."],
    ["servicios/validador.py",
     "Convierte y valida lo que escribe el usuario. validar_entero() rechaza texto y numeros fuera de rango; validar_rut() aplica Modulo 11; validar_fecha_futura() exige formato y fecha posterior a hoy. Las funciones pedir_* repiten la pregunta.",
     "Si se llamara a int() directamente sobre lo que escribe el usuario, el programa se cae con ValueError. Ese es el caso P19 del guion de pruebas."],
    ["servicios/indicador_dolar.py",
     "Consulta mindicador.cl con timeout de cinco segundos, valida el codigo de respuesta y toma el valor mas reciente de la serie. Guarda ese valor como respaldo y entrega el ultimo conocido cuando la consulta falla.",
     "Sin timeout el programa puede quedar colgado; sin capturar la excepcion, el sistema se cae cuando no hay internet."],
    ["servicios/codigos.py",
     "Genera los codigos de clientes y productos. Recorre los existentes con una expresion regular, toma el mayor y propone el siguiente, verificando que no exista antes de asignarlo.",
     "Si no se verificara la existencia, se intentaria insertar un codigo duplicado y la clave primaria rechazaria el registro."],
    ["model/cliente.py",
     "Modela al comprador. El atributo identificador se valida en el setter: RUT con Modulo 11 o correo con expresion regular. Si el dato es invalido, la excepcion se lanza al construir el objeto.",
     "Si la validacion se moviera al menu, cualquier otro programa que use la clase Cliente podria crear clientes invalidos."],
    ["model/pedido.py",
     "Es la transaccion: agrega lineas con el precio congelado, calcula el total con los fletes, confirma verificando el stock, registra el pago descontando el inventario y autoriza el despacho. Aqui viven las dos reglas de negocio.",
     "Si se descontara el stock antes de confirmar, un pedido rechazado por falta de stock habria bajado el inventario igual."],
    ["model/producto_fisico.py y sus subtipos",
     "ProductoFisico calcula el flete con peso, volumen y distancia. ProductoDigital y ProductoServicio sobrescriben procesar_entrega(). ProductoElectronica hereda de ProductoFisico y sobrescribe calcular_precio_final().",
     "Si se reemplazara el polimorfismo por un if sobre el tipo dentro de Pedido, cada tipo nuevo obligaria a modificar Pedido y la rubrica lo evalua como nivel En desarrollo."],
]


def build() -> None:
    e = crear_estilos()
    documento = DocumentoGuion(str(SALIDA))
    c: list = []

    # ----------------------------------------------------------- portada
    c += [
        Spacer(1, 28 * mm),
        Paragraph("ClickAndGo", e["cubierta_titulo"]),
        Paragraph("Revision oral del codigo", e["cubierta_sub"]),
        Paragraph("Guion de la defensa", e["cubierta_doc"]),
        Spacer(1, 10 * mm),
    ]
    datos_portada = [
        ("Asignatura", "Programacion Orientada a Objeto Seguro - TI3V21"),
        ("Evaluacion", "Sumativa N3 - Unidad 4: desarrollo de soluciones en Python"),
        ("Instancia", "Revision oral del codigo: 10 minutos de presentacion y 5 de preguntas"),
        ("Fecha y hora", "Martes 13 de octubre de 2026, 21:30 hrs"),
        ("Lugar", "Laboratorio A403 (grupo 05, E-commerce)"),
        ("Integrantes", "Miguel Troncoso y Alexandy Remicinthe"),
        ("Seccion", "114-2A-F2 - INACAP Puente Alto"),
        ("Docente", "Michael Arjel"),
        ("Repositorio", "https://github.com/MiguelTroncoso/ecommerce"),
    ]
    filas = [[Paragraph(f"<b>{etiqueta}</b>", e["cubierta_dato"]),
              Paragraph(valor, e["cubierta_dato"])] for etiqueta, valor in datos_portada]
    tabla_portada = Table(filas, colWidths=[38 * mm, 118 * mm], hAlign="CENTER")
    tabla_portada.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDE),
        ("TEXTCOLOR", (0, 0), (0, -1), AZUL_CLARO),
    ]))
    c += [
        tabla_portada,
        Spacer(1, 14 * mm),
        Paragraph(
            "Este documento es el guion de lo que cada integrante dice y muestra en pantalla. No se lee "
            "completo en voz alta: esta escrito para ensayarlo, para saber que archivo abrir en cada "
            "momento y para responder las preguntas del docente.",
            e["nota"],
        ),
        PageBreak(),
    ]

    # ------------------------------------- 1. evaluacion y checklist
    c += [
        Paragraph("1. Que se evalua y como llegar preparados", e["h1"]),
        Paragraph(
            "La nota tiene dos mitades. Los 21 puntos de producto se asignan una vez por equipo y "
            "corresponden al recorrido del codigo: ubicar los requisitos, seguir una operacion completa, "
            "mostrar los cambios de la retroalimentacion y explicar la seguridad. Los 21 puntos de defensa "
            "son individuales: el docente elige una parte del codigo al azar y cada integrante la explica "
            "por separado, predice el efecto de un cambio, justifica una decision de seguridad y da un "
            "ejemplo concreto de uso de inteligencia artificial.",
            e["cuerpo"],
        ),
        Paragraph("1.1 Checklist antes de entrar al laboratorio", e["h2"]),
        Paragraph("El editor con el repositorio abierto debe estar listo antes del inicio del bloque.", e["cuerpo"]),
        Paragraph("- Llegar 15 minutos antes y abrir el repositorio en el editor.", e["vineta"]),
        Paragraph("- Actualizar el repositorio: no debe quedar ningun cambio sin guardar.", e["vineta"]),
        Paragraph("- Cerrar notificaciones, correo y cualquier pestana que no se use.", e["vineta"]),
        Paragraph("- Dejar el terminal cerrado: en esta evaluacion el programa no se ejecuta.", e["vineta"]),
        Paragraph("- Fijar el zoom de fuente en un tamano legible desde el fondo de la sala.", e["vineta"]),
        Paragraph("- Abrir las pestanas en el orden de la presentacion.", e["vineta"]),
        Paragraph("- Tener a mano este guion, en papel o en el celular.", e["vineta"]),
        Paragraph("1.2 Pestanas que deben quedar abiertas, en este orden", e["h2"]),
        tabla([
            ["#", "Archivo", "Para que se muestra"],
            ["1", "main.py", "Menu, orquestacion y captura de las excepciones de negocio"],
            ["2", "model/producto.py", "Clase abstracta: contrato de los cuatro subtipos"],
            ["3", "model/pedido.py", "Polimorfismo, confirmacion, pago, despacho y las dos reglas"],
            ["4", "model/cliente.py", "Validacion obligatoria del RUT o correo en el setter"],
            ["5", "model/excepciones.py", "Las excepciones propias del negocio"],
            ["6", "dao/conexion.py", "Esquema de tablas y consultas parametrizadas"],
            ["7", "dao/pedido_dao.py", "Transaccion con lineas de detalle"],
            ["8", "servicios/validador.py", "Requisito no funcional: validacion de entradas"],
            ["9", "servicios/indicador_dolar.py", "Requisito no funcional: API con timeout y respaldo"],
            ["10", "servicios/codigos.py", "Mejora: codigos automaticos de clientes y productos"],
            ["11", "README.md", "Decisiones de seguridad y uso de IA"],
        ], e, [10 * mm, 46 * mm, 100 * mm]),
        PageBreak(),
    ]

    # --------------------------------------------- 2. reparto
    c += [
        Paragraph("2. Reparto de la presentacion", e["h1"]),
        Paragraph(
            "Los dos integrantes presentan y los dos responden preguntas. El reparto busca que cada uno "
            "tenga una parte del modelo, una de persistencia y una de seguridad.",
            e["cuerpo"],
        ),
        tabla([
            ["Bloque", "Tiempo", "Quien", "Contenido", "Archivos que abre"],
            ["1", "0:00 - 1:00", "Miguel", "Apertura, arquitectura de cuatro capas y agenda", "main.py"],
            ["2", "1:00 - 3:30", "Alexandy", "Los cinco requisitos funcionales de la ficha",
             "producto.py, producto_fisico.py, cliente.py, pedido.py, producto_electronica.py"],
            ["3", "3:30 - 5:30", "Miguel", "Recorrido completo: registrar el pago de un pedido",
             "main.py, pedido.py, producto.py, pedido_dao.py, producto_dao.py"],
            ["4", "5:30 - 7:30", "Alexandy", "Requisitos no funcionales y decisiones de seguridad",
             "validador.py, indicador_dolar.py, conexion.py, trabajador.py"],
            ["5", "7:30 - 9:30", "Miguel", "Cambios de la retroalimentacion y uso de IA",
             "codigos.py, consola.py, README.md"],
            ["6", "9:30 - 10:00", "Ambos", "Cierre y ofrecimiento de preguntas", "-"],
        ], e, [16 * mm, 20 * mm, 19 * mm, 52 * mm, 49 * mm]),
        Paragraph(
            "Si el docente pide cambiar el orden, se pueden invertir los bloques 2 y 4 sin problema: los "
            "dos integrantes conocen los cuatro bloques.",
            e["nota"],
        ),
        PageBreak(),
    ]

    # ---------------------------------- 3. guion minuto a minuto
    c += [Paragraph("3. Guion minuto a minuto", e["h1"])]
    c += [
        Paragraph("Bloque 1 (0:00 - 1:00) - Miguel: apertura y arquitectura", e["h2"]),
        Paragraph(
            "Buenas noches, profesor. Somos Miguel Troncoso y Alexandy Remicinthe, del grupo 5, caso "
            "E-commerce: ClickAndGo. El repositorio que esta en pantalla es el mismo de la evaluacion "
            "anterior, corregido con la retroalimentacion que recibimos.",
            e["guion"],
        ),
        Paragraph(
            "Para ubicarnos rapido, el sistema tiene cuatro capas. <b>main.py</b> es el menu de consola: "
            "pide los datos y captura los errores de negocio. La carpeta <b>servicios/</b> valida las "
            "entradas, genera los codigos automaticos y consulta la API del dolar. La carpeta "
            "<b>model/</b> tiene las clases del negocio, con las reglas y las excepciones propias. Y la "
            "carpeta <b>dao/</b> guarda todo en SQLite con consultas parametrizadas. Ninguna clase del "
            "modelo contiene SQL: si cambia la base de datos, solo se modifica la capa dao.",
            e["guion"],
        ),
        Paragraph(
            "En estos diez minutos vamos a hacer cuatro cosas: ubicar los requisitos en el codigo, seguir "
            "una operacion completa hasta la consulta SQL, mostrar que cambiamos despues de la "
            "retroalimentacion y explicar como el codigo protege los datos. Alexandy parte ubicando los "
            "cinco requisitos de la ficha.",
            e["guion"],
        ),
        Paragraph("En pantalla: main.py, el menu y el bloque que captura las excepciones.", e["cuerpo"]),
        Paragraph("Bloque 2 (1:00 - 3:30) - Alexandy: los cinco requisitos funcionales", e["h2"]),
        Paragraph(
            "Gracias, Miguel. La ficha de ClickAndGo pide cinco requisitos funcionales y estan en cinco "
            "lugares concretos del codigo.",
            e["guion"],
        ),
        Paragraph(
            "<b>Primero, tres subtipos con un metodo que se comporta distinto en cada uno.</b> En "
            "<b>model/producto.py</b> esta la clase abstracta Producto, que declara "
            "<i>procesar_entrega()</i> sin implementarlo. Los tres subtipos heredan con "
            "<i>super().__init__()</i> y lo sobrescriben: <i>ProductoFisico</i> genera un despacho por "
            "transporte y calcula el flete con peso, volumen y distancia; <i>ProductoDigital</i> entrega "
            "un enlace y una licencia con flete cero; y <i>ProductoServicio</i> agenda una visita tecnica "
            "para una fecha futura.",
            e["guion"],
        ),
        Paragraph(
            "<b>Segundo, un dato con validacion obligatoria.</b> Esta en <b>model/cliente.py</b>, en el "
            "setter del atributo <i>identificador</i>. Si el tipo es RUT, se valida con el algoritmo "
            "Modulo 11 en <i>validar_rut()</i>; si es correo, se valida con expresion regular. La "
            "validacion esta en el modelo y no en el menu: aunque otro programa use estas clases, no se "
            "puede construir un cliente con un RUT invalido.",
            e["guion"],
        ),
        Paragraph(
            "<b>Tercero, una transaccion con lineas de detalle.</b> Un pedido es la clase <i>Pedido</i> y "
            "cada linea es un <i>DetallePedido</i>, que congela la cantidad y el precio unitario al "
            "momento de la venta. La relacion es de composicion: si se elimina el pedido, sus lineas se "
            "eliminan con el, y en la base de datos eso esta declarado con <i>ON DELETE CASCADE</i>. En "
            "<b>dao/pedido_dao.py</b> el pedido y sus lineas se insertan dentro de una sola transaccion: o "
            "se guardan todos o no se guarda ninguno.",
            e["guion"],
        ),
        Paragraph(
            "<b>Cuarto, dos reglas que impiden una operacion, cada una con su excepcion propia.</b> En "
            "<b>model/pedido.py</b>, <i>confirmar_pedido()</i> recorre las lineas y si no hay stock "
            "suficiente lanza <i>StockInsuficienteError</i>. Y <i>despachar()</i> verifica el permiso del "
            "trabajador y luego que el pedido este pagado; si no lo esta, lanza <i>PedidoNoPagadoError</i>. "
            "Las dos excepciones estan en <b>model/excepciones.py</b> y se capturan en main.py con "
            "<i>except ClickAndGoError</i>, que informa el problema y devuelve el control al menu.",
            e["guion"],
        ),
        Paragraph(
            "<b>Quinto, un precio que depende de un indicador externo.</b> La clase "
            "<i>ProductoElectronica</i> hereda de ProductoFisico y guarda su costo en dolares. Su metodo "
            "<i>calcular_precio_final()</i> multiplica ese valor por el dolar del dia. Ese valor lo "
            "entrega <b>servicios/indicador_dolar.py</b>, que consulta mindicador.cl con la libreria "
            "requests. En el pedido se usa ese precio congelado en la linea de detalle.",
            e["guion"],
        ),
        Paragraph(
            "Esos son los cinco requisitos funcionales. Miguel va a seguir ahora una operacion completa, "
            "desde el menu hasta la consulta SQL.",
            e["guion"],
        ),
        Paragraph("Bloque 3 (3:30 - 5:30) - Miguel: recorrido completo de una operacion", e["h2"]),
        Paragraph(
            "Vamos a seguir una sola operacion, de principio a fin: registrar el pago de un pedido. La "
            "idea es mostrar que cada capa tiene una responsabilidad distinta.",
            e["guion"],
        ),
        Paragraph(
            "<b>Paso 1, el menu.</b> En <b>main.py</b>, <i>_registrar_pago()</i> le pide al usuario que "
            "elija un pedido de la lista y llama al objeto del modelo. El menu no calcula nada: solo pide "
            "datos y arma el objeto.",
            e["guion"],
        ),
        Paragraph(
            "<b>Paso 2, el modelo.</b> En <b>model/pedido.py</b>, <i>registrar_pago()</i> primero llama a "
            "<i>confirmar_pedido()</i>. Eso es importante: si no hay stock, la excepcion se lanza antes de "
            "tocar el inventario, y por eso el stock no cambia cuando la operacion se rechaza. Solo si la "
            "confirmacion pasa, se descuenta el stock de cada linea.",
            e["guion"],
        ),
        Paragraph(
            "<b>Paso 3, los productos.</b> Cada producto descuenta su propio stock en "
            "<i>descontar_stock()</i>, en <b>model/producto.py</b>. Ese metodo vuelve a verificar el stock "
            "antes de rebajarlo: la regla esta en el modelo, no en la interfaz.",
            e["guion"],
        ),
        Paragraph(
            "<b>Pasos 4 y 5, la persistencia.</b> El pedido queda con estado PAGADO y la capa dao lo "
            "guarda: <i>actualizar_estado()</i> en <b>dao/pedido_dao.py</b> escribe el estado y "
            "<i>actualizar_stock()</i> en <b>dao/producto_dao.py</b> escribe el nuevo stock de cada producto.",
            e["guion"],
        ),
        Paragraph("<b>Paso 6, la consulta SQL.</b> Esta es la sentencia que realmente guarda el cambio:", e["guion"]),
        Paragraph("UPDATE productos SET stock = :stock WHERE id_producto = :id", e["codigo"]),
        Paragraph(
            "Los dos puntos indican un parametro enlazado. El valor que escribio el usuario viaja como "
            "dato, nunca como parte del texto de la sentencia. Eso es lo que evita la inyeccion SQL. Con "
            "esto, Alexandy muestra los requisitos no funcionales y la seguridad.",
            e["guion"],
        ),
        Paragraph("Bloque 4 (5:30 - 7:30) - Alexandy: no funcionales y seguridad", e["h2"]),
        Paragraph("Ademas de los cinco requisitos funcionales, mostramos dos no funcionales.", e["guion"]),
        Paragraph(
            "<b>Validacion de entradas.</b> Esta en <b>servicios/validador.py</b>. Las funciones "
            "<i>pedir_entero()</i>, <i>pedir_decimal()</i> y <i>pedir_fecha_futura()</i> piden el dato en "
            "un ciclo: si el valor no cumple el tipo, el formato o el rango, muestran el mensaje y vuelven "
            "a preguntar. El programa no se cae. Los setters del modelo validan lo mismo por su lado: "
            "stock no negativo, precio no negativo y fecha futura para un servicio. En el guion de "
            "pruebas, el caso P19 escribe letras donde va un numero y el caso P08 escribe un correo incompleto.",
            e["guion"],
        ),
        Paragraph(
            "<b>Continuidad si la API falla.</b> Esta en <b>servicios/indicador_dolar.py</b>. La consulta "
            "usa <i>requests.get</i> con <i>timeout=5</i>: el sistema no puede quedarse colgado esperando a "
            "un servidor lento. Se valida que la respuesta traiga la serie del dolar y, si algo falla, se "
            "lanza <i>IndicadorNoDisponibleError</i>. El metodo <i>valor_para_calculo()</i> usa entonces el "
            "ultimo valor guardado en datos/dolar_respaldo.json y avisa al operador. Eso es el caso P17: se "
            "corta el internet y el sistema informa y sigue funcionando.",
            e["guion"],
        ),
        Paragraph(
            "<b>Consultas parametrizadas.</b> Estan en <b>dao/conexion.py</b> y en todos los DAO. Todas "
            "las sentencias usan parametros enlazados y la conexion activa <i>PRAGMA foreign_keys = ON</i> "
            "para que se respeten las claves foraneas. Si alguien escribiera comillas o un punto y coma en "
            "un campo, ese texto se guarda como dato y no se interpreta como SQL.",
            e["guion"],
        ),
        Paragraph(
            "<b>Autenticacion y permisos.</b> En <b>model/trabajador.py</b> las contrasenas se guardan con "
            "PBKDF2-HMAC-SHA256 con sal aleatoria, nunca en texto plano. Y los permisos se resuelven por "
            "rol: el <i>EncargadoBodega</i> puede despachar pero no modificar el catalogo, y si lo intenta "
            "se lanza <i>SinPermisoError</i>. Miguel cierra con los cambios que hicimos despues de la "
            "retroalimentacion.",
            e["guion"],
        ),
        Paragraph("Bloque 5 (7:30 - 9:30) - Miguel: cambios de la retroalimentacion y uso de IA", e["h2"]),
        Paragraph(
            "En la evaluacion anterior recibimos observaciones y las corregimos en el repositorio. Los "
            "cambios estan en el README, en la seccion de cambios incorporados.",
            e["guion"],
        ),
        Paragraph(
            "<b>El cambio principal es que los codigos ya no se escriben.</b> Antes habia que inventar el "
            "identificador del producto y del cliente, por ejemplo PROD-E01, y eso era lento y permitia "
            "repetir codigos. Ahora el sistema los genera: C01 para clientes y F01, D01, S01 y E01 para "
            "los cuatro tipos de producto. El codigo esta en <b>servicios/codigos.py</b>, en la clase "
            "<i>GeneradorCodigos</i>: consulta los codigos existentes, calcula el mayor y propone el "
            "siguiente, verificando que este libre antes de asignarlo.",
            e["guion"],
        ),
        Paragraph(
            "<b>El segundo cambio es la interfaz.</b> Ahora los listados son tablas con encabezado y "
            "columnas alineadas, y se elige un registro por su numero en la lista, no escribiendo el "
            "codigo. Los formularios muestran el paso en el que van, por ejemplo [2 de 7], y al terminar "
            "aparece un panel con el resumen y el codigo asignado. Los mensajes se distinguen: [OK] para "
            "un exito, [!] para un aviso y [i] para informacion. Todo eso esta en <b>servicios/consola.py</b>.",
            e["guion"],
        ),
        Paragraph(
            "<b>Sobre el uso de inteligencia artificial.</b> La usamos como apoyo y documentamos que "
            "hicimos con cada sugerencia. Adoptamos usar <i>sqlite3.Row</i> para leer las columnas por "
            "nombre en vez de por indice, porque asi un cambio en el orden del SELECT no rompe el codigo. "
            "Modificamos la sugerencia de consumir la API: la version original no tenia tiempo maximo de "
            "espera y la nuestra usa timeout y captura las fallas. Y descartamos dos: resolver el tipo de "
            "producto con <i>if</i> en vez de polimorfismo, porque la rubrica pide polimorfismo, y guardar "
            "la contrasena con MD5, porque no es seguro para contrasenas; usamos PBKDF2 con sal.",
            e["guion"],
        ),
        Paragraph("Bloque 6 (9:30 - 10:00) - cierre", e["h2"]),
        Paragraph(
            "Para cerrar: los cinco requisitos funcionales y los dos no funcionales estan ubicados en el "
            "codigo, la operacion completa se puede seguir desde el menu hasta la consulta SQL, los "
            "cambios de la retroalimentacion estan en el repositorio y los datos estan protegidos con "
            "consultas parametrizadas, validacion de entradas y manejo de la falla de la API. El "
            "repositorio es publico y esta en pantalla. Gracias, quedamos atentos a sus preguntas.",
            e["guion"],
        ),
        PageBreak(),
    ]

    # --------------------------------------- 4. transiciones
    c += [
        Paragraph("4. Frases de transicion", e["h1"]),
        Paragraph("Tener estas frases a mano evita silencios largos entre bloques.", e["cuerpo"]),
        tabla([
            ["Cuando", "Frase"],
            ["De arquitectura a requisitos",
             "Con la arquitectura clara, vamos a ubicar los cinco requisitos de la ficha en el codigo."],
            ["De requisitos a recorrido",
             "Ya sabemos donde esta cada requisito; ahora seguimos una operacion completa hasta la base de datos."],
            ["De recorrido a seguridad",
             "Vimos como se guarda; ahora vemos como el codigo protege esos datos."],
            ["De seguridad a cambios",
             "Ahora les mostramos que corregimos despues de la retroalimentacion de la evaluacion anterior."],
            ["De cambios al cierre",
             "Con eso cerramos: requisitos ubicados, operacion recorrida, cambios incorporados y datos protegidos."],
            ["Si no saben algo",
             "Eso no lo trabajamos de esa forma; en nuestro codigo se resuelve en la clase o funcion que les muestro ahora."],
        ], e, [40 * mm, 116 * mm]),
        PageBreak(),
    ]

    # ------------------------------------ 5. banco de preguntas
    c += [
        Paragraph("5. Banco de preguntas del docente", e["h1"]),
        Paragraph(
            "La defensa es individual: el docente elige una parte del codigo y pregunta a cada integrante "
            "por separado. Las respuestas deben ser cortas y siempre acompanadas del archivo en pantalla.",
            e["cuerpo"],
        ),
    ]
    filas = [["Pregunta", "Respuesta preparada"]]
    for pregunta, respuesta in PREGUNTAS:
        filas.append([f"<b>{pregunta}</b>", respuesta])
    c += [tabla(filas, e, [58 * mm, 98 * mm]), PageBreak()]

    # --------------------------------------- 6. fichas por archivo
    c += [
        Paragraph("6. Fichas rapidas: si te toca explicar este archivo", e["h1"]),
        Paragraph(
            "Para cada archivo clave: que hace y que pasaria si se cambia algo. Es la parte que el docente "
            "pregunta de forma individual.",
            e["cuerpo"],
        ),
    ]
    for titulo, que_hace, si_cambia in FICHAS:
        c.append(KeepTogether([
            Paragraph(titulo, e["h3"]),
            Paragraph(f"<b>Que hace:</b> {que_hace}", e["cuerpo"]),
            Paragraph(f"<b>Si se cambia:</b> {si_cambia}", e["cuerpo"]),
        ]))
    c.append(PageBreak())

    # ------------------------------------------- 7. errores y cierre
    c += [
        Paragraph("7. Errores que hay que evitar", e["h1"]),
        Paragraph("- Prometer que el codigo hace algo que no se puede mostrar en pantalla.", e["vineta"]),
        Paragraph("- Leer las diapositivas: el material de apoyo es el codigo, no la presentacion.", e["vineta"]),
        Paragraph("- Hablar de memoria sin abrir el archivo que se esta nombrando.", e["vineta"]),
        Paragraph("- Decir 'no se' sin ofrecer la parte que si se conoce: siempre se puede mostrar donde esta y para que sirve.", e["vineta"]),
        Paragraph("- Explicar las funciones del companero sin que le corresponda: se puede complementar, pero sin interrumpir.", e["vineta"]),
        Paragraph("- Usar terminos que no se puedan definir si el docente pregunta, por ejemplo polimorfismo o inyeccion SQL.", e["vineta"]),
        Paragraph("8. Cierre", e["h1"]),
        Paragraph(
            "La presentacion queda en diez minutos con este reparto y sobran cinco para las preguntas. Los "
            "cuatro puntos que hay que dejar dichos, si por tiempo algo queda fuera, son: donde esta cada "
            "requisito, como se sigue una operacion completa hasta la base de datos, que se corrigio "
            "despues de la retroalimentacion y como el codigo protege los datos.",
            e["cuerpo"],
        ),
        Paragraph(
            "La defensa individual depende de conocer los once archivos de la lista de pestanas. Con las "
            "fichas de la seccion 6 y el banco de preguntas de la seccion 5, cualquiera de los dos puede "
            "responder por cualquier parte del codigo.",
            e["cuerpo"],
        ),
    ]

    documento.build(c)
    print(f"Generado: {SALIDA}")


if __name__ == "__main__":
    build()
