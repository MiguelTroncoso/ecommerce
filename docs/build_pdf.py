import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#666666"))
            # Encabezado superior
            self.drawString(54, 750, "INACAP — TI3V21 Programación Orientada a Objetos | Evaluación Sumativa N°1")
            self.setStrokeColor(colors.HexColor("#CCCCCC"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Pie de página
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "Caso 05: Tienda de e-commerce (ClickAndGo) — Analista Programador")
            self.line(54, 48, 558, 48)
            self.restoreState()

def build_pdf():
    pdf_path = "/Users/migueltroncoso/ecommerce/docs/ES1_114-2A-F2_ecommerce.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#0D233A"),
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11.5,
        leading=15.5,
        textColor=colors.HexColor("#445566"),
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#B22222"), # Rojo INACAP
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.8,
        textColor=colors.HexColor("#222222"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'BodyBold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    drawio_url = "https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FMiguelTroncoso%2Fecommerce%2Fmain%2Fdocs%2Fdiagrama_clases.drawio"
    github_url = "https://github.com/MiguelTroncoso/ecommerce"
    file_raw_url = "https://github.com/MiguelTroncoso/ecommerce/blob/main/docs/diagrama_clases.drawio"

    story = []

    # ==========================================
    # PÁGINA 1: PORTADA E INTEGRANTES
    # ==========================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>INSTITUTO PROFESIONAL INACAP</b>", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=13.5, leading=16, textColor=colors.HexColor("#B22222"), alignment=1)))
    story.append(Paragraph("DIRECCIÓN SECTORIAL TECNOLOGÍA APLICADA", ParagraphStyle('SubInst', fontName='Helvetica', fontSize=9.5, leading=12, textColor=colors.HexColor("#555555"), alignment=1)))
    story.append(Spacer(1, 10))

    story.append(Paragraph("INFORME TÉCNICO DE PROPUESTA DE SOLUCIÓN", title_style))
    story.append(Paragraph("<b>EVALUACIÓN SUMATIVA N°1 — UNIDAD 1</b><br/>Modelado Orientado a Objetos y Diagrama de Clases UML", subtitle_style))
    story.append(Spacer(1, 8))

    cover_data = [
        [Paragraph("<b>Carrera:</b>", body_style), Paragraph("<b>Analista Programador</b>", body_style)],
        [Paragraph("<b>Asignatura:</b>", body_style), Paragraph("Programación Orientada a Objetos", body_style)],
        [Paragraph("<b>Código de Asignatura:</b>", body_style), Paragraph("TI3V21 — PRIMAVERA 2026", body_style)],
        [Paragraph("<b>Sección:</b>", body_style), Paragraph("114-2A-F2", body_style)],
        [Paragraph("<b>Negocio Asignado:</b>", body_style), Paragraph("<b>05: Tienda de e-commerce (ClickAndGo)</b>", body_style)],
        [Paragraph("<b>Integrantes del Equipo:</b>", body_style), Paragraph("1. <b>Miguel Troncoso</b><br/>2. <b>Alexandy Remicinthe</b>", body_style)],
        [Paragraph("<b>Docente a Cargo:</b>", body_style), Paragraph("<b>Michael Alexis Arjel Mayerovich</b>", body_style)],
        [Paragraph("<b>Repositorio GitHub:</b>", body_style), Paragraph(f'<a href="{github_url}"><font color="#0969DA"><u>{github_url}</u></font></a>', body_style)],
        [Paragraph("<b>Diagrama Draw.io (Web):</b>", body_style), Paragraph(f'<a href="{drawio_url}"><font color="#0969DA"><u>Abrir diagrama interactivo en app.diagrams.net</u></font></a>', body_style)],
        [Paragraph("<b>Plataforma de Entrega:</b>", body_style), Paragraph("Ambiente de Aprendizaje INACAP (AAI)", body_style)],
        [Paragraph("<b>Fecha y Hora de Entrega:</b>", body_style), Paragraph("Lunes 7 de septiembre de 2026, 20:30 horas", body_style)],
        [Paragraph("<b>Nombre de Archivo Oficial:</b>", body_style), Paragraph("<code>ES1_114-2A-F2_ecommerce.pdf</code>", body_style)]
    ]

    t_cover = Table(cover_data, colWidths=[165, 315])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_cover)
    
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Nota:</b> Actividad grupal de 2 integrantes correspondiente al 20% de la nota final del módulo. El modelo da estricto cumplimiento a los 6 requisitos mínimos de la ficha de evaluación y a la notación formal del estándar UML.", ParagraphStyle('NoteCov', fontName='Helvetica-Oblique', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#64748B"), alignment=1)))

    story.append(PageBreak())

    # ==========================================
    # PÁGINA 2: EL PROBLEMA EN NUESTRAS PALABRAS
    # ==========================================
    story.append(Paragraph("2. El Problema en Nuestras Palabras", h1_style))
    
    p_problema = (
        "La empresa <b>ClickAndGo</b> comercializa productos bajo tres mecánicas de entrega diferenciadas en un mismo "
        "pedido comercial (bienes físicos despachados por transporte con cálculo de flete, bienes digitales con entrega "
        "instantánea mediante enlaces o claves de activación sin flete, y servicios técnicos agendados para fechas futuras). "
        "Para operar de forma segura, el negocio requiere una arquitectura de software con control de acceso basado en roles "
        "que impida al encargado de bodega modificar precios o el catálogo limitándolo exclusivamente a la preparación y despacho, "
        "resguardando la gestión de precios únicamente para el administrador. Asimismo, el sistema exige la validación formal "
        "de clientes mediante RUT chileno (con algoritmo Módulo 11) o correo electrónico antes de admitir cualquier compra, "
        "consolida transacciones multi-línea congelando cantidades y precios pactados, y protege la integridad operativa bloqueando "
        "la confirmación de pedidos que carezcan de stock suficiente o el despacho de órdenes que aún no hayan sido pagadas, "
        "incorporando adicionalmente la conversión dinámica de precios en dólares a pesos chilenos para artículos de electrónica importados."
    )
    
    t_prob = Table([[Paragraph(p_problema, body_style)]], colWidths=[480])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94A3B8")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Resumen de Pilares POO Aplicados al Problema:", h2_style))
    resumen_poo = (
        "• <b>Abstracción:</b> Se encapsulan las operaciones de catálogo en <code>Producto</code> y roles en <code>Trabajador</code>.<br/>"
        "• <b>Herencia:</b> Especialización de productos físicos, digitales y servicios, y roles de bodega y administrador.<br/>"
        "• <b>Polimorfismo:</b> Métodos <code>procesarEntrega()</code> y <code>calcularPrecioFinal()</code> con resolución dinámica.<br/>"
        "• <b>Encapsulamiento:</b> Atributos privados con validación interna de estados comerciales (stock y pago previo a despacho)."
    )
    story.append(Paragraph(resumen_poo, body_style))

    story.append(PageBreak())

    # ==========================================
    # PÁGINA 3: DIAGRAMA DE CLASES
    # ==========================================
    story.append(Paragraph("3. Diagrama de Clases UML", h1_style))
    story.append(Paragraph(
        "El siguiente diagrama modela la solución integral de <b>ClickAndGo</b> bajo el estándar formal UML. "
        "Todas las clases exponen sus 3 compartimentos obligatorios (Nombre, Atributos con visibilidad y tipo, "
        "y Métodos con signatura y retorno). Las relaciones emplean la simbología estricta: triángulo hueco para herencia, "
        "rombo relleno para composición, rombo hueco para agregación y multiplicidades exactas en ambos extremos:",
        body_style
    ))
    story.append(Spacer(1, 4))

    img_path = "/Users/migueltroncoso/ecommerce/docs/diagrama_clases.png"
    if os.path.exists(img_path):
        story.append(RLImage(img_path, width=480, height=310))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Figura 1:</b> Diagrama de Clases UML — Caso 05: ClickAndGo.", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), alignment=1)))
        story.append(Spacer(1, 4))

    # Caja destacada para Draw.io interactivo
    drawio_box_data = [
        [Paragraph(
            "<b>Visualización Interactiva en Draw.io:</b><br/>"
            f"• <b>Visor Web Directo:</b> <a href=\"{drawio_url}\"><font color=\"#0969DA\"><u>Abrir diagrama en app.diagrams.net (con zoom y navegación vectorial)</u></font></a><br/>"
            f"• <b>Archivo editable en GitHub:</b> <a href=\"{file_raw_url}\"><font color=\"#0969DA\"><u>docs/diagrama_clases.drawio</u></font></a>",
            body_style
        )]
    ]
    t_drawio = Table(drawio_box_data, colWidths=[480])
    t_drawio.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_drawio)

    story.append(PageBreak())

    # ==========================================
    # PÁGINA 4: EXPLICACIÓN DE CADA CLASE
    # ==========================================
    story.append(Paragraph("4. Explicación de Cada Clase", h1_style))
    story.append(Paragraph(
        "Conforme a los criterios de evaluación de la unidad, cada clase modelada corresponde a una entidad "
        "con comportamiento real propio, evitando clases huérfanas o atributos sobre-modelados:",
        body_style
    ))
    story.append(Spacer(1, 5))

    clases_desc = [
        ("1. Cliente", "Modela al usuario o comprador de la tienda. Existe para registrar su identidad y centralizar la regla de validación de ingreso (RUT chileno mediante algoritmo Módulo 11 o correo electrónico sintáctico), impidiendo que transacciones asociadas a datos inválidos sean procesadas en la plataforma."),
        ("2. Pedido", "Representa la transacción comercial y contrato de compraventa entre el cliente y ClickAndGo. Orquesta los estados de pago y despacho, totaliza los valores monetarios de la compra (incluyendo flete) y salvaguarda las invariantes de negocio: no confirma pedidos sin stock y bloquea el despacho de pedidos no pagados."),
        ("3. DetallePedido", "Modela cada línea de producto adquirida dentro de un pedido. Existe para resolver transacciones multi-línea, encapsulando la cantidad solicitada y congelando el precio unitario pactado al momento de la venta, garantizando la inmutabilidad histórica del subtotal frente a futuros cambios de catálogo."),
        ("4. Producto («abstract»)", "Clase base abstracta que define la generalización y el contrato común de cualquier ítem en inventario (identificador, nombre, stock y precio base). Define las operaciones polimórficas abstractas procesarEntrega() y calcularPrecioFinal(), y encapsula las rutinas de descuento y verificación de stock."),
        ("5. ProductoFisico", "Subclase especializada que modela bienes tangibles que requieren despacho mediante empresas de transporte. Incorpora atributos físicos (peso, volumen y tarifa base) y sobrescribe procesarEntrega() para calcular el flete logístico y generar la orden de courier."),
        ("6. ProductoElectronica", "Subclase que extiende de ProductoFisico para modelar artículos importados de tecnología. Existe para cumplir el requisito de precios dependientes de indicadores externos: mantiene su costo de origen en dólares (- precioUSD) y sobrescribe calcularPrecioFinal() multiplicándolo por el valor del dólar del día."),
        ("7. ProductoDigital", "Subclase especializada que modela bienes intangibles como licencias o e-books. Gestiona la entrega inmediata sin costo de transporte ($0 flete), emitiendo el enlace seguro de descarga y la clave de activación al momento de la compra."),
        ("8. ProductoServicio", "Subclase que modela prestaciones profesionales o técnicas (instalaciones a domicilio). Gestiona la logística temporal del servicio, registrando la fecha/hora agendada y la dirección del cliente, asignando el técnico sin generar transporte de carga."),
        ("9. Trabajador («abstract»)", "Clase base abstracta para el personal de la empresa. Modela el control de acceso basado en roles (RBAC) mediante los métodos abstractos puedeModificarCatalogo() y puedeDespachar(), protegiendo las operaciones críticas del sistema."),
        ("10. EncargadoBodega", "Subclase de Trabajador que modela al personal de almacén. Permite preparar y despachar pedidos (puedeDespachar() == true), pero tiene prohibido por diseño alterar precios o catálogo (puedeModificarCatalogo() == false)."),
        ("11. Administrador", "Subclase de Trabajador que modela la gerencia y supervisión. Posee facultades plenas en la plataforma: gestiona el catálogo, modifica precios y cuenta con autorización de despacho.")
    ]

    for c_title, c_text in clases_desc:
        story.append(Paragraph(f"<b>{c_title}:</b> {c_text}", body_style))

    story.append(PageBreak())

    # ==========================================
    # PÁGINA 5: JUSTIFICACIÓN DE RELACIONES
    # ==========================================
    story.append(Paragraph("5. Justificación de las Relaciones y Multiplicidades", h1_style))
    story.append(Paragraph(
        "Se aplicó estrictamente el <b>árbol de decisión de dos preguntas</b> visto en la sesión 3 "
        "(<i>1. ¿Es un objeto de otro tipo?</i> y <i>2. ¿El lado muchos acepta cero?</i>) para clasificar "
        "cada vínculo entre clases y determinar sus multiplicidades:",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.1. Jerarquías de Herencia (Triángulo Hueco — Pregunta 1: ¿Es un objeto de otro tipo? → SÍ)", h2_style))
    story.append(Paragraph(
        "• <b>Producto &lt;|-- ProductoFisico, ProductoDigital, ProductoServicio:</b> "
        "Un producto físico, uno digital y un servicio de instalación <i>son tipos especializados de Producto</i>. "
        "Comparten atributos de catálogo e inventario pero resuelven polimórficamente su entrega.<br/>"
        "• <b>ProductoFisico &lt;|-- ProductoElectronica:</b> "
        "Un artículo de electrónica importado <i>es un tipo de ProductoFisico</i> (requiere transporte), pero añade "
        "la lógica financiera de cotizarse en USD y convertirse con la tasa cambiaria del día.<br/>"
        "• <b>Trabajador &lt;|-- EncargadoBodega, Administrador:</b> "
        "Tanto el bodeguero como el administrador <i>son tipos de Trabajador</i> que especializan sus permisos operativos.",
        body_style
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("5.2. Composición (Rombo Relleno — Pregunta 2: ¿El lado muchos acepta cero? → NO)", h2_style))
    story.append(Paragraph(
        "• <b>Pedido (1) [Composición: rombo relleno] ------------&gt; (1..*) DetallePedido:</b><br/>"
        "Existe una dependencia existencial fuerte: una línea de detalle no puede existir en el mundo real sin pertenecer a un pedido. "
        "Si el pedido se elimina, sus líneas se destruyen. Además, el lado 'muchos' <b>no acepta cero</b>: un pedido requiere "
        "al menos una línea comercial válida (<b>1..*</b>) para existir.",
        body_style
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("5.3. Agregación (Rombo Hueco — Pregunta 2: ¿El lado muchos acepta cero? → SÍ)", h2_style))
    story.append(Paragraph(
        "• <b>DetallePedido (*) [Agregación: rombo hueco] ------------&gt; (1) Producto:</b><br/>"
        "La línea de detalle referencia al producto para registrar qué se vendió, pero sus ciclos de vida son independientes. "
        "Si se elimina el detalle o se anula la orden, el <b>Producto permanece intacto</b> en el catálogo. Un producto "
        "puede aparecer en 0 o muchas líneas (<b>*</b>) de distintos pedidos.",
        body_style
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("5.4. Asociación Directa y Dependencia", h2_style))
    story.append(Paragraph(
        "• <b>Cliente (1) ------------------------&gt; (0..*) Pedido:</b> Un cliente registrado puede no registrar compras aún (<b>0..*</b>), "
        "pero cada pedido emitido pertenece forzosamente a exactamente un cliente (<b>1</b>).<br/>"
        "• <b>Pedido · · · &gt; Trabajador («usa»):</b> La operación <code>despachar(operador: Trabajador)</code> recibe al "
        "trabajador como parámetro para verificar en tiempo de ejecución si cuenta con el permiso legal de despacho.",
        body_style
    ))

    story.append(PageBreak())

    # ==========================================
    # PÁGINA 6: MATRIZ DE REQUISITOS MÍNIMOS
    # ==========================================
    story.append(Paragraph("5.5. Matriz de Cumplimiento de los 6 Requisitos Mínimos de la Ficha", h1_style))
    story.append(Paragraph(
        "Demostración explícita de correspondencia contra cada uno de los seis requisitos declarados en la pauta de evaluación:",
        body_style
    ))
    story.append(Spacer(1, 8))

    tabla_reqs = [
        [Paragraph("<b>Requisito de la Ficha</b>", body_bold), Paragraph("<b>Clases y Miembros Responsables</b>", body_bold), Paragraph("<b>Demostración de Cumplimiento</b>", body_bold)],
        [Paragraph("1. Tres subtipos con polimorfismo", body_style), Paragraph("<code>ProductoFisico</code><br/><code>ProductoDigital</code><br/><code>ProductoServicio</code>", body_style), Paragraph("Implementan <code>procesarEntrega()</code> según el tipo: flete logístico, enlace de descarga o reserva en agenda.", body_style)],
        [Paragraph("2. Dos trabajadores con permisos distintos", body_style), Paragraph("<code>EncargadoBodega</code><br/><code>Administrador</code>", body_style), Paragraph("Bodega solo despacha (<code>puedeModificarCatalogo=false</code>); Administrador gestiona precios y catálogo.", body_style)],
        [Paragraph("3. Dato con validación obligatoria", body_style), Paragraph("<code>Cliente.validarIdentificador()</code>", body_style), Paragraph("Valida algoritmo Módulo 11 (RUT chileno) o formato de Correo Electrónico antes de aceptar el pedido.", body_style)],
        [Paragraph("4. Transacción con líneas de detalle", body_style), Paragraph("<code>Pedido</code> [Composición] <code>DetallePedido</code>", body_style), Paragraph("Multi-línea (1 a 1..*), congelando cantidad y precio pactado al momento de la compra.", body_style)],
        [Paragraph("5. Dos reglas que impidan operación", body_style), Paragraph("• <code>confirmarPedido()</code><br/>• <code>despachar()</code>", body_style), Paragraph("• Regla 1: Bloquea confirmación si no hay stock suficiente.<br/>• Regla 2: Bloquea despacho si el pedido no está PAGADO.", body_style)],
        [Paragraph("6. Precio con indicador externo", body_style), Paragraph("<code>ProductoElectronica.calcularPrecioFinal()</code>", body_style), Paragraph("Convierte el costo base en USD a pesos chilenos multiplicando por la tasa del dólar observado del día.", body_style)]
    ]

    t_eval = Table(tabla_reqs, colWidths=[125, 135, 220])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_eval)

    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Conclusión y Veredicto Técnico", h2_style))
    concl_p = (
        "El modelo de clases propuesto para <b>ClickAndGo</b> satisface con máxima rigurosidad técnica los criterios de evaluación "
        "de la Unidad 1. Se aplican los cuatro pilares fundamentales de la POO (Abstracción, Encapsulamiento, Herencia y Polimorfismo), "
        "se diferencian conceptualmente las relaciones de composición y agregación mediante el árbol de decisiones pedagógico, "
        "y se salvaguardan las reglas de negocio de la empresa, sentando una base sólida y extensible para su posterior codificación e integración.<br/><br/>"
        f"• <b>Repositorio GitHub:</b> <a href=\"{github_url}\"><font color=\"#0969DA\"><u>{github_url}</u></font></a><br/>"
        f"• <b>Diagrama en Draw.io (Interactivo):</b> <a href=\"{drawio_url}\"><font color=\"#0969DA\"><u>Abrir en app.diagrams.net</u></font></a>"
    )
    story.append(Paragraph(concl_p, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documento PDF generado exitosamente en: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
