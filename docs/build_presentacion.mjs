/**
 * Genera la presentacion de apoyo para la revision oral del codigo
 * (Evaluacion Sumativa N3 - INACAP TI3V21).
 *
 * Uso:
 *   CODEX_PRIMARY_RUNTIME_NODE_MODULES=<node_modules> node docs/build_presentacion.mjs
 */

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const nodeModules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if (!nodeModules) {
  throw new Error("Falta CODEX_PRIMARY_RUNTIME_NODE_MODULES");
}
const requireFromRuntime = createRequire(path.join(nodeModules, "__runtime__.cjs"));
const { Presentation, PresentationFile } = requireFromRuntime("@oai/artifact-tool");

const DIR = path.dirname(fileURLToPath(import.meta.url));
const SALIDA = path.join(DIR, "ES3_114-2A-F2_presentacion.pptx");
const SALIDA_PNG = path.join(DIR, "..", "tmp", "presentacion");

const AZUL = "#0D233A";
const AZUL_CLARO = "#1C4E80";
const ROJO = "#D63426";
const GRIS = "#F2F5F9";
const BORDE = "#D6DEE8";
const TEXTO = "#1F2933";
const VERDE = "#1A7F4B";
const BLANCO = "#FFFFFF";

const W = 1280;
const H = 720;
const MARCO = { left: 64, top: 56, width: 1152 };

function caja(slide, opciones) {
  return slide.shapes.add({
    geometry: opciones.geometry ?? "textbox",
    name: opciones.name,
    position: {
      left: opciones.left,
      top: opciones.top,
      width: opciones.width,
      height: opciones.height,
    },
    fill: opciones.fill ?? "none",
    line: opciones.line ?? { style: "solid", fill: "none", width: 0 },
    ...(opciones.borderRadius ? { borderRadius: opciones.borderRadius } : {}),
  });
}

function texto(slide, contenido, opciones) {
  const shape = caja(slide, { ...opciones, name: opciones.name });
  shape.text = contenido;
  shape.text.style = {
    fontSize: opciones.fontSize ?? 18,
    bold: opciones.bold ?? false,
    color: opciones.color ?? TEXTO,
    lineSpacing: opciones.lineSpacing ?? 1.15,
    ...(opciones.italic ? { italic: true } : {}),
  };
  if (opciones.alignment) {
    shape.text.alignment = opciones.alignment;
  }
  return shape;
}

function encabezado(slide, kicker, titulo, bajada) {
  texto(slide, kicker, {
    left: MARCO.left, top: 40, width: MARCO.width, height: 22,
    fontSize: 13, bold: true, color: ROJO,
  });
  texto(slide, titulo, {
    left: MARCO.left, top: 64, width: MARCO.width, height: 44,
    fontSize: 32, bold: true, color: AZUL,
  });
  if (bajada) {
    texto(slide, bajada, {
      left: MARCO.left, top: 110, width: MARCO.width, height: 26,
      fontSize: 15, color: "#5A6B7C",
    });
  }
}

function tabla(slide, valores, opciones) {
  const table = slide.tables.add({
    rows: valores.length,
    columns: valores[0].length,
    left: opciones.left,
    top: opciones.top,
    width: opciones.width,
    height: opciones.height ?? 40 + valores.length * (opciones.rowHeight ?? 34),
    values: valores,
    columnTracks: opciones.columnTracks,
  });
  for (let fila = 0; fila < valores.length; fila += 1) {
    for (let columna = 0; columna < valores[0].length; columna += 1) {
      const celda = table.getCell(fila, columna);
      celda.fill = fila === 0 ? AZUL : (fila % 2 === 0 ? GRIS : BLANCO);
      celda.text.style = {
        fontSize: fila === 0 ? 13.5 : 13,
        bold: fila === 0,
        color: fila === 0 ? BLANCO : TEXTO,
      };
    }
  }
  table.borders.assign({ style: "solid", fill: BORDE, width: 1 });
  return table;
}

async function main() {
  const p = Presentation.create({ slideSize: { width: W, height: H } });
  await fs.mkdir(SALIDA_PNG, { recursive: true });

  // ---------------------------------------------------------------- 1
  {
    const slide = p.slides.add();
    slide.background.fill = AZUL;
    texto(slide, "ClickAndGo", {
      left: 80, top: 150, width: 1120, height: 90,
      fontSize: 68, bold: true, color: BLANCO, alignment: "center",
    });
    texto(slide, "Revision oral del codigo", {
      left: 80, top: 250, width: 1120, height: 40,
      fontSize: 28, color: "#9FC0E0", alignment: "center",
    });
    texto(slide, "Evaluacion Sumativa N3  |  Unidad 4: desarrollo de soluciones de software en Python", {
      left: 80, top: 296, width: 1120, height: 28,
      fontSize: 15, color: "#7FA3C4", alignment: "center",
    });
    slide.shapes.add({
      geometry: "rect", position: { left: 540, top: 350, width: 200, height: 3 },
      fill: ROJO, line: { style: "solid", fill: "none", width: 0 },
    });
    texto(slide, "Miguel Troncoso  y  Alexandy Remicinthe", {
      left: 80, top: 380, width: 1120, height: 30,
      fontSize: 20, bold: true, color: BLANCO, alignment: "center",
    });
    texto(slide, "TI3V21 - Seccion 114-2A-F2  |  INACAP Puente Alto  |  Martes 13 de octubre de 2026, 21:30 hrs - Laboratorio A403", {
      left: 80, top: 418, width: 1120, height: 24,
      fontSize: 14, color: "#7FA3C4", alignment: "center",
    });
    slide.speakerNotes.text =
      "Buenas noches. Somos Miguel Troncoso y Alexandy Remicinthe, del caso 05, E-commerce ClickAndGo. " +
      "En los proximos diez minutos vamos a recorrer el codigo del sistema: donde esta cada requisito, " +
      "el camino completo de una operacion hasta la base de datos, que cambiamos despues de la retroalimentacion " +
      "de la evaluacion anterior y como el codigo protege los datos.";
  }

  // ---------------------------------------------------------------- 2
  {
    const slide = p.slides.add();
    encabezado(slide, "AGENDA", "Lo que vamos a mostrar en el codigo", "Diez minutos, cuatro bloques");
    const bloques = [
      ["1", "Donde esta cada requisito", "Cinco funcionales y dos no funcionales, con archivo, clase o funcion."],
      ["2", "El camino de una operacion completa", "Desde el menu en main.py hasta la consulta SQL que guarda."],
      ["3", "Que cambio despues de la retroalimentacion", "Codigos automaticos y rediseno de la interfaz."],
      ["4", "Como el codigo protege los datos", "Consultas parametrizadas, validacion y manejo de la falla de la API."],
    ];
    bloques.forEach(([numero, titulo, detalle], indice) => {
      const top = 175 + indice * 108;
      caja(slide, {
        geometry: "roundRect", left: MARCO.left, top, width: 66, height: 66,
        fill: AZUL, line: { style: "solid", fill: "none", width: 0 },
      }).text = numero;
      texto(slide, titulo, {
        left: MARCO.left + 90, top: top + 2, width: 700, height: 26,
        fontSize: 20, bold: true, color: AZUL,
      });
      texto(slide, detalle, {
        left: MARCO.left + 90, top: top + 32, width: 900, height: 24,
        fontSize: 15, color: "#5A6B7C",
      });
    });
    slide.speakerNotes.text =
      "El recorrido tiene cuatro bloques. Primero ubicamos los requisitos en el codigo, despues seguimos una " +
      "operacion completa hasta el SQL, luego explicamos los cambios que hicimos tras la retroalimentacion y " +
      "cerramos con las decisiones de seguridad.";
  }

  // ---------------------------------------------------------------- 3
  {
    const slide = p.slides.add();
    encabezado(slide, "ARQUITECTURA", "Cuatro capas, una responsabilidad cada una", "Cada capa se puede cambiar sin tocar las demas");
    const capas = [
      ["main.py", "Menu de consola", "Pide los datos y captura los errores de negocio.", AZUL_CLARO],
      ["servicios/", "Validacion, codigos y API", "Valida entradas, genera codigos y consulta el dolar.", "#2E6DA4"],
      ["model/", "Reglas del negocio", "Clases, herencia, polimorfismo y excepciones propias.", "#3F88C5"],
      ["dao/", "Persistencia", "CRUD en SQLite con consultas parametrizadas.", "#59A5D8"],
    ];
    capas.forEach(([archivo, titulo, detalle, color], indice) => {
      const top = 168 + indice * 92;
      caja(slide, {
        geometry: "roundRect", left: MARCO.left, top, width: 1152, height: 76,
        fill: GRIS, line: { style: "solid", fill: BORDE, width: 1 },
      });
      caja(slide, {
        geometry: "rect", left: MARCO.left, top, width: 8, height: 76,
        fill: color, line: { style: "solid", fill: "none", width: 0 },
      });
      texto(slide, archivo, {
        left: MARCO.left + 30, top: top + 8, width: 200, height: 28,
        fontSize: 20, bold: true, color: AZUL,
      });
      texto(slide, titulo, {
        left: MARCO.left + 250, top: top + 10, width: 300, height: 24,
        fontSize: 16, bold: true, color: color,
      });
      texto(slide, detalle, {
        left: MARCO.left + 250, top: top + 38, width: 860, height: 24,
        fontSize: 14, color: "#5A6B7C",
      });
    });
    texto(slide, "Datos guardados en datos/clickandgo.db  |  Las tablas se crean solas al iniciar", {
      left: MARCO.left, top: 560, width: 1152, height: 24,
      fontSize: 14, italic: true, color: "#5A6B7C",
    });
    slide.speakerNotes.text =
      "El sistema tiene cuatro capas. main.py es el menu, servicios valida y consume la API, model tiene las " +
      "reglas del negocio y dao guarda en SQLite. La separacion importa porque ninguna clase del modelo contiene SQL: " +
      "si cambia la base de datos, solo se toca la capa dao.";
  }

  // ---------------------------------------------------------------- 4
  {
    const slide = p.slides.add();
    encabezado(slide, "REQUISITOS FUNCIONALES", "Los cinco requisitos de la ficha, ubicados en el codigo",
      "Cada fila es un requisito; cada archivo es el que abrimos en el editor");
    tabla(slide, [
      ["Requisito", "Archivo", "Clase o funcion"],
      ["1. Tres subtipos con un metodo que cambia", "model/producto_fisico.py, producto_digital.py, producto_servicio.py", "procesar_entrega() sobrescrito"],
      ["2. Dato con validacion obligatoria", "model/cliente.py", "Cliente.identificador (setter) y validar_rut()"],
      ["3. Transaccion con lineas de detalle", "model/pedido.py  +  dao/pedido_dao.py", "Pedido.agregar_linea() y PedidoDAO.crear()"],
      ["4. Dos reglas con excepcion propia", "model/pedido.py  +  model/excepciones.py", "confirmar_pedido() y despachar()"],
      ["5. Precio con indicador externo", "model/producto_electronica.py  +  servicios/indicador_dolar.py", "calcular_precio_final() y obtener_valor_dolar()"],
    ], {
      left: MARCO.left, top: 168, width: 1152, rowHeight: 62,
      columnTracks: [{ mode: "fr", value: 3.1 }, { mode: "fr", value: 4.2 }, { mode: "fr", value: 3.1 }],
    });
    texto(slide, "En cada caso abrimos el archivo y mostramos la linea exacta.", {
      left: MARCO.left, top: 560, width: 1152, height: 24,
      fontSize: 14, italic: true, color: "#5A6B7C",
    });
    slide.speakerNotes.text =
      "Esta tabla es el mapa que vamos a usar. Requisito uno: los subtipos heredan de Producto con super y " +
      "sobrescriben procesar_entrega. Requisito dos: el identificador del cliente se valida en el setter con " +
      "modulo 11 o correo. Requisito tres: el pedido compone DetallePedido y se guarda con sus lineas. " +
      "Requisito cuatro: las dos reglas tienen excepcion propia. Requisito cinco: la electronica se cotiza con " +
      "el dolar del dia desde mindicador.cl.";
  }

  // ---------------------------------------------------------------- 5
  {
    const slide = p.slides.add();
    encabezado(slide, "REQUISITOS NO FUNCIONALES", "Dos requisitos que no se ven en el menu, pero sostienen el sistema",
      "La rubrica pide al menos dos: mostramos estos y, ademas, las consultas parametrizadas");
    const tarjetas = [
      ["Validacion de entradas", "servicios/validador.py",
        ["pedir_entero(), pedir_decimal() y pedir_fecha_futura() reintentan sin caer.",
         "Cliente.identificador, Producto.stock y ProductoServicio.fecha_agendada validan en el setter.",
         "El caso P19 del guion de pruebas escribe letras donde va un numero y el programa sigue."]],
      ["Continuidad si la API falla", "servicios/indicador_dolar.py",
        ["requests.get con timeout=5: la consulta no puede colgar el programa.",
         "Si falla, se lanza IndicadorNoDisponibleError y se usa el ultimo valor guardado.",
         "El caso P17 del guion de pruebas desconecta el wifi y el sistema avisa y continua."]],
    ];
    tarjetas.forEach(([titulo, archivo, puntos], indice) => {
      const left = MARCO.left + indice * 590;
      caja(slide, {
        geometry: "roundRect", left, top: 175, width: 562, height: 330,
        fill: GRIS, line: { style: "solid", fill: BORDE, width: 1 },
      });
      texto(slide, titulo, { left: left + 26, top: 198, width: 510, height: 30, fontSize: 21, bold: true, color: AZUL });
      texto(slide, archivo, { left: left + 26, top: 232, width: 510, height: 22, fontSize: 14, italic: true, color: ROJO });
      puntos.forEach((punto, i) => {
        texto(slide, "-  " + punto, {
          left: left + 26, top: 268 + i * 68, width: 500, height: 62,
          fontSize: 14, color: TEXTO,
        });
      });
    });
    slide.speakerNotes.text =
      "Ademas de los cinco requisitos funcionales mostramos dos no funcionales. Primero la validacion de " +
      "entradas: cada dato se valida por tipo, formato y rango antes de usarse, y si esta mal el programa avisa " +
      "y vuelve a preguntar, nunca se cae. Segundo la continuidad ante fallas: la API del dolar tiene tiempo " +
      "maximo de espera y respaldo local. Si no hay internet, el sistema informa y sigue funcionando.";
  }

  // ---------------------------------------------------------------- 6
  {
    const slide = p.slides.add();
    encabezado(slide, "RECORRIDO COMPLETO", "El camino de una operacion: registrar el pago de un pedido",
      "Del menu a la consulta SQL, capa por capa");
    const pasos = [
      ["1", "main.py", "_registrar_pago()", "El menu elige el pedido y llama al objeto del modelo."],
      ["2", "model/pedido.py", "Pedido.registrar_pago()", "Primero confirma el stock y despues descuenta."],
      ["3", "model/producto.py", "descontar_stock()", "Cada producto valida y rebaja su propio stock."],
      ["4", "dao/pedido_dao.py", "actualizar_estado()", "Guarda el nuevo estado del pedido."],
      ["5", "dao/producto_dao.py", "actualizar_stock()", "Guarda el stock por producto."],
      ["6", "SQLite", "UPDATE ... WHERE", "Consulta parametrizada: UPDATE productos SET stock = :stock WHERE id_producto = :id"],
    ];
    pasos.forEach(([numero, archivo, funcion, detalle], indice) => {
      const top = 160 + indice * 78;
      caja(slide, {
        geometry: "roundRect", left: MARCO.left, top, width: 44, height: 44,
        fill: indice === 5 ? VERDE : AZUL, line: { style: "solid", fill: "none", width: 0 },
      }).text = numero;
      texto(slide, archivo, { left: MARCO.left + 64, top: top + 2, width: 250, height: 22, fontSize: 15, bold: true, color: AZUL });
      texto(slide, funcion, { left: MARCO.left + 64, top: top + 24, width: 380, height: 20, fontSize: 13, color: ROJO });
      texto(slide, detalle, { left: MARCO.left + 460, top: top + 8, width: 690, height: 42, fontSize: 13.5, color: TEXTO });
    });
    slide.speakerNotes.text =
      "Seguimos una operacion completa: registrar el pago. El menu llama a registrar_pago en el modelo. " +
      "Ese metodo primero confirma que hay stock: por eso el stock no cambia si la confirmacion falla. " +
      "Si esta todo bien, cada producto descuenta su stock, el pedido queda PAGADO y recien ahi la capa dao " +
      "escribe en la base de datos con un UPDATE parametrizado. Es importante notar que el modelo decide y el " +
      "dao solo guarda.";
  }

  // ---------------------------------------------------------------- 7
  {
    const slide = p.slides.add();
    encabezado(slide, "POLIMORFISMO", "Un mismo metodo, cuatro comportamientos distintos",
      "Pedido.procesar_despacho_entregas() recorre las lineas sin preguntar el tipo de producto");
    const tipos = [
      ["ProductoFisico", "Despacho por transporte", "Calcula flete por peso, volumen y distancia.", "#3F88C5"],
      ["ProductoDigital", "Entrega inmediata", "Entrega el enlace y la licencia, con flete cero.", "#59A5D8"],
      ["ProductoServicio", "Agenda tecnica", "Registra fecha futura, direccion y duracion.", "#7FB8DD"],
      ["ProductoElectronica", "Hereda de ProductoFisico", "Mismo despacho, pero cotiza en USD con el dolar del dia.", "#2E6DA4"],
    ];
    tipos.forEach(([nombre, titulo, detalle, color], indice) => {
      const left = MARCO.left + (indice % 2) * 590;
      const top = 172 + Math.floor(indice / 2) * 176;
      caja(slide, {
        geometry: "roundRect", left, top, width: 562, height: 156,
        fill: BLANCO, line: { style: "solid", fill: color, width: 2 },
      });
      texto(slide, nombre, { left: left + 24, top: top + 18, width: 510, height: 26, fontSize: 18, bold: true, color: AZUL });
      texto(slide, titulo, { left: left + 24, top: top + 50, width: 510, height: 22, fontSize: 14, bold: true, color: color });
      texto(slide, detalle, { left: left + 24, top: top + 78, width: 510, height: 60, fontSize: 14, color: TEXTO });
    });
    texto(slide, "for detalle in self._detalles:  resultados.append(detalle.producto.procesar_entrega(detalle))", {
      left: MARCO.left, top: 540, width: 1152, height: 40,
      fontSize: 15, color: AZUL, fill: GRIS, alignment: "center",
    });
    slide.speakerNotes.text =
      "Aqui esta el polimorfismo. La clase Producto define procesar_entrega como metodo abstracto y cada subtipo " +
      "lo sobrescribe: el fisico genera despacho y flete, el digital entrega un enlace con flete cero, el servicio " +
      "agenda una visita y la electronica hereda el despacho del fisico pero cotiza en dolares. El pedido recorre " +
      "sus lineas con un for y llama al metodo: no hay un if preguntando el tipo. Si mañana se agrega un tipo nuevo, " +
      "no hay que modificar Pedido.";
  }

  // ---------------------------------------------------------------- 8
  {
    const slide = p.slides.add();
    encabezado(slide, "REGLAS DE NEGOCIO", "Dos reglas que impiden una operacion", "Cada una tiene su excepcion propia y se captura de forma especifica");
    const reglas = [
      ["Regla 1", "No confirmar un pedido sin stock", "model/pedido.py - confirmar_pedido()",
        "raise StockInsuficienteError(producto.nombre, detalle.cantidad, producto.stock)",
        "El stock no cambia porque el descuento ocurre recien al registrar el pago."],
      ["Regla 2", "No despachar un pedido impago", "model/pedido.py - despachar(operador)",
        "raise PedidoNoPagadoError(self._id_pedido, self._estado_pago)",
        "Antes de esa linea se verifica con SinPermisoError que el rol pueda despachar."],
    ];
    reglas.forEach(([etiqueta, titulo, ubicacion, codigo, nota], indice) => {
      const top = 168 + indice * 208;
      caja(slide, {
        geometry: "roundRect", left: MARCO.left, top, width: 1152, height: 188,
        fill: GRIS, line: { style: "solid", fill: BORDE, width: 1 },
      });
      texto(slide, etiqueta, { left: MARCO.left + 24, top: top + 16, width: 120, height: 24, fontSize: 13, bold: true, color: ROJO });
      texto(slide, titulo, { left: MARCO.left + 150, top: top + 14, width: 620, height: 26, fontSize: 19, bold: true, color: AZUL });
      texto(slide, ubicacion, { left: MARCO.left + 150, top: top + 44, width: 620, height: 22, fontSize: 13, italic: true, color: AZUL_CLARO });
      texto(slide, codigo, {
        left: MARCO.left + 24, top: top + 78, width: 1104, height: 36,
        fontSize: 14, color: AZUL, fill: BLANCO,
      });
      texto(slide, nota, { left: MARCO.left + 24, top: top + 124, width: 1104, height: 44, fontSize: 14, color: TEXTO });
    });
    texto(slide, "Las excepciones se capturan en main.py:  except ClickAndGoError -> avisa y vuelve al menu", {
      left: MARCO.left, top: 596, width: 1152, height: 26,
      fontSize: 14, bold: true, color: ROJO, alignment: "center",
    });
    slide.speakerNotes.text =
      "Las dos reglas de la ficha son las dos unicas que impiden una operacion comercial. La primera: al confirmar " +
      "un pedido se recorre cada linea y si no hay stock se lanza StockInsuficienteError. Como el descuento ocurre " +
      "solo al registrar el pago, el stock queda intacto. La segunda: al despachar se verifica el permiso del " +
      "trabajador y que el pago este registrado; si no lo esta, se lanza PedidoNoPagadoError. Ambas excepciones " +
      "heredan de ClickAndGoError y se capturan en main.py, asi el programa informa y sigue funcionando.";
  }

  // ---------------------------------------------------------------- 9
  {
    const slide = p.slides.add();
    encabezado(slide, "INDICADOR EXTERNO", "El precio de la electronica depende del dolar del dia",
      "servicios/indicador_dolar.py usa la libreria oficial requests");
    const items = [
      ["Consulta", "requests.get('https://mindicador.cl/api/dolar', timeout=5)", "La serie del dolar viene en el JSON; se toma el valor mas reciente."],
      ["Conversion", "ProductoElectronica.calcular_precio_final(valor_dolar)", "precio_usd * valor_dolar, redondeado a pesos."],
      ["Si la API falla", "except (RequestException, ValueError, KeyError)", "Se lanza IndicadorNoDisponibleError con el motivo."],
      ["Continuidad", "ultimo_valor_conocido()", "Se usa el respaldo en datos/dolar_respaldo.json y se avisa al operador."],
    ];
    items.forEach(([titulo, codigo, detalle], indice) => {
      const top = 172 + indice * 106;
      texto(slide, titulo, { left: MARCO.left, top: top + 6, width: 200, height: 26, fontSize: 16, bold: true, color: AZUL });
      texto(slide, codigo, {
        left: MARCO.left + 210, top: top + 2, width: 942, height: 34,
        fontSize: 13.5, color: AZUL, fill: GRIS,
      });
      texto(slide, detalle, { left: MARCO.left + 210, top: top + 40, width: 942, height: 24, fontSize: 13.5, color: "#5A6B7C" });
    });
    slide.speakerNotes.text =
      "El quinto requisito es el precio con indicador externo. La electronica importada se cotiza en dolares y se " +
      "convierte con el valor del dia que entrega mindicador.cl. Usamos la libreria requests con tiempo maximo de " +
      "espera de cinco segundos. Si la API no responde, se guarda el ultimo valor conocido y el sistema lo informa " +
      "y sigue funcionando: ese es el caso P17 del guion de pruebas.";
  }

  // ---------------------------------------------------------------- 10
  {
    const slide = p.slides.add();
    encabezado(slide, "SEGURIDAD", "Como el codigo protege los datos", "Cada mecanismo evita un riesgo concreto");
    tabla(slide, [
      ["Mecanismo", "Donde esta", "Riesgo que evita"],
      ["Consultas parametrizadas", "dao/conexion.py y todos los DAO", "Inyeccion SQL: el texto del usuario nunca se concatena en la sentencia."],
      ["Validacion de entradas", "servicios/validador.py y setters del modelo", "Datos invalidos guardados o programa detenido por un error de tipo."],
      ["Tiempo maximo de espera", "indicador_dolar.py (timeout=5)", "Que una API lenta deje el sistema colgado esperando respuesta."],
      ["Excepciones propias de negocio", "model/excepciones.py y main.py", "Operaciones inseguras y caidas del programa ante un error esperado."],
      ["Contrasena con PBKDF2 y salt", "model/trabajador.py", "Lectura de contrasenas si alguien obtiene el archivo de la base de datos."],
      ["Control de acceso por rol", "encargado_bodega.py y administrador.py", "Que un rol sin autorizacion modifique precios o catalogo."],
    ], {
      left: MARCO.left, top: 172, width: 1152, rowHeight: 56,
      columnTracks: [{ mode: "fr", value: 2.6 }, { mode: "fr", value: 3.4 }, { mode: "fr", value: 5.0 }],
    });
    slide.speakerNotes.text =
      "Resumimos la seguridad en seis mecanismos, cada uno con el riesgo que evita. Lo mas importante: las " +
      "consultas son parametrizadas, por lo que aunque el usuario escriba comillas o punto y coma, ese texto nunca " +
      "se interpreta como SQL. Las contrasenas se guardan con PBKDF2 y salt aleatorio, y los permisos se resuelven " +
      "por rol con excepcion propia. Si me preguntan que pasaria si quitamos una validacion, la respuesta es que " +
      "el dato invalido llegaria al modelo o a la base de datos y el sistema perderia integridad.";
  }

  // ---------------------------------------------------------------- 11
  {
    const slide = p.slides.add();
    encabezado(slide, "RETROALIMENTACION ES2", "Que cambio en el codigo despues de la evaluacion anterior",
      "Los seis cambios y donde se ven");
    tabla(slide, [
      ["Observacion recibida", "Cambio realizado", "Donde se ve"],
      ["Habia que escribir el codigo de productos y clientes", "El sistema los genera: C01, F01, D01, S01, E01", "servicios/codigos.py"],
      ["Era incomodo operar escribiendo codigos", "Listas numeradas: se elige con el numero, o con 0 se cancela", "servicios/consola.py"],
      ["No se sabia en que paso iba el registro", "Formularios con contador [1/7] y panel de resumen", "main.py"],
      ["Las listas eran texto suelto", "Tablas con encabezado y columnas alineadas", "servicios/consola.py"],
      ["Los mensajes se veian todos iguales", "[OK], [!], [i] y [X], con color en terminal", "servicios/consola.py"],
      ["El menu no explicaba cada opcion", "Descripcion breve por opcion y operador activo", "main.py"],
    ], {
      left: MARCO.left, top: 172, width: 1152, rowHeight: 58,
      columnTracks: [{ mode: "fr", value: 4.2 }, { mode: "fr", value: 5.2 }, { mode: "fr", value: 2.6 }],
    });
    slide.speakerNotes.text =
      "Este es el punto que pide la rubrica: que cambio despues de la retroalimentacion. Los seis cambios estan en " +
      "el repositorio y cada uno tiene su prueba. Los dos mas visibles son los codigos automaticos y el rediseno de " +
      "la interfaz, que es lo que voy a mostrar ahora en el editor.";
  }

  // ---------------------------------------------------------------- 12
  {
    const slide = p.slides.add();
    encabezado(slide, "MEJORA PRINCIPAL", "Los codigos ya no se escriben: los asigna el sistema",
      "servicios/codigos.py - clase GeneradorCodigos");
    caja(slide, {
      geometry: "roundRect", left: MARCO.left, top: 172, width: 556, height: 190,
      fill: "#FBECEA", line: { style: "solid", fill: ROJO, width: 1.5 },
    });
    texto(slide, "Antes", { left: MARCO.left + 24, top: 190, width: 500, height: 28, fontSize: 18, bold: true, color: ROJO });
    texto(slide, "Registrar producto\n  Identificador: PROD-E01\n  Nombre: Monitor 4K\n  Precio USD: 250", {
      left: MARCO.left + 24, top: 226, width: 500, height: 116, fontSize: 15, color: TEXTO,
    });
    caja(slide, {
      geometry: "roundRect", left: MARCO.left + 596, top: 172, width: 556, height: 190,
      fill: "#E9F5EE", line: { style: "solid", fill: VERDE, width: 1.5 },
    });
    texto(slide, "Ahora", { left: MARCO.left + 620, top: 190, width: 500, height: 28, fontSize: 18, bold: true, color: VERDE });
    texto(slide, "Registrar producto\n  [1/7] Tipo: 4 - Electronica\n  [2/7] Nombre: Monitor 4K\n  [7/7] Garantia: 12\n  Codigo asignado: E02", {
      left: MARCO.left + 620, top: 226, width: 500, height: 116, fontSize: 15, color: TEXTO,
    });
    tabla(slide, [
      ["Tipo de registro", "Prefijo", "Ejemplo"],
      ["Cliente", "C", "C01, C02, C03"],
      ["Producto fisico", "F", "F01, F02"],
      ["Producto digital", "D", "D01, D02"],
      ["Servicio tecnico", "S", "S01, S02"],
      ["Electronica importada", "E", "E01, E02"],
      ["Pedido", "PED-", "PED-1001"],
    ], {
      left: MARCO.left, top: 388, width: 1152, rowHeight: 36,
      columnTracks: [{ mode: "fr", value: 2 }, { mode: "fr", value: 1 }, { mode: "fr", value: 2 }],
    });
    slide.speakerNotes.text =
      "Esta es la mejora principal. Antes el operador tenia que inventar y escribir el codigo del producto, lo que " +
      "era lento y permitia duplicados o errores de tipeo. Ahora el sistema consulta el ultimo codigo usado en la " +
      "base de datos, calcula el siguiente y verifica que este libre antes de asignarlo. El usuario solo escribe el " +
      "nombre y los datos. En el codigo esta en servicios/codigos.py, clase GeneradorCodigos, y se usa al crear el " +
      "cliente, el producto y el pedido.";
  }

  // ---------------------------------------------------------------- 13
  {
    const slide = p.slides.add();
    encabezado(slide, "USO DE IA", "Que propuso la IA y como lo evaluamos", "Un ejemplo concreto de cada decision");
    tabla(slide, [
      ["Sugerencia de la IA", "Decision", "Razon tecnica"],
      ["Acceder a las columnas de SQLite por nombre con sqlite3.Row", "Adoptada", "Un cambio en el orden del SELECT ya no rompe la construccion de los objetos."],
      ["Consumir la API con requests.get(URL) sin tiempo maximo de espera", "Modificada", "Se agrego timeout y captura especifica de fallas: la rubrica exige continuidad del sistema."],
      ["Resolver el tipo de producto con if/elif dentro de Pedido", "Descartada", "La rubrica indica que reemplazar el polimorfismo por if queda en nivel En desarrollo."],
      ["Guardar la contrasena con hashlib.md5", "Descartada", "MD5 no es apto para contrasenas; se uso PBKDF2-HMAC-SHA256 con salt aleatorio."],
    ], {
      left: MARCO.left, top: 176, width: 1152, rowHeight: 78,
      columnTracks: [{ mode: "fr", value: 5.4 }, { mode: "fr", value: 1.8 }, { mode: "fr", value: 5.2 }],
    });
    slide.speakerNotes.text =
      "Sobre el uso de inteligencia artificial: la usamos como apoyo, no como reemplazo. Hay un ejemplo concreto de " +
      "cada caso. Adoptamos el acceso por nombre de columna en SQLite. Modificamos la consulta a la API agregandole " +
      "tiempo maximo de espera. Y descartamos dos sugerencias: resolver el tipo con if, porque la rubrica pide " +
      "polimorfismo, y guardar la contrasena con MD5, porque no es seguro. Todo esta documentado en el README.";
  }

  // ---------------------------------------------------------------- 14
  {
    const slide = p.slides.add();
    encabezado(slide, "CIERRE", "Como nos repartimos la presentacion", "Todo el codigo esta en el repositorio publico");
    const reparto = [
      ["Miguel Troncoso", "Arquitectura, recorrido completo de la operacion y cambios de la retroalimentacion",
        "main.py, model/pedido.py, servicios/codigos.py"],
      ["Alexandy Remicinthe", "Los cinco requisitos funcionales, requisitos no funcionales y seguridad",
        "model/cliente.py, producto_fisico.py, dao/, servicios/"],
    ];
    reparto.forEach(([nombre, tarea, archivos], indice) => {
      const top = 180 + indice * 140;
      caja(slide, {
        geometry: "roundRect", left: MARCO.left, top, width: 1152, height: 120,
        fill: GRIS, line: { style: "solid", fill: BORDE, width: 1 },
      });
      texto(slide, nombre, { left: MARCO.left + 26, top: top + 18, width: 320, height: 28, fontSize: 20, bold: true, color: AZUL });
      texto(slide, tarea, { left: MARCO.left + 360, top: top + 20, width: 770, height: 46, fontSize: 15, color: TEXTO });
      texto(slide, archivos, { left: MARCO.left + 360, top: top + 72, width: 770, height: 24, fontSize: 13, italic: true, color: ROJO });
    });
    texto(slide, "Gracias. Quedamos atentos a sus preguntas.", {
      left: MARCO.left, top: 480, width: 1152, height: 34,
      fontSize: 22, bold: true, color: AZUL, alignment: "center",
    });
    texto(slide, "github.com/MiguelTroncoso/ecommerce   |   inacap.superflash.site", {
      left: MARCO.left, top: 520, width: 1152, height: 26,
      fontSize: 14, color: "#5A6B7C", alignment: "center",
    });
    slide.speakerNotes.text =
      "Para cerrar: Miguel presenta la arquitectura, el recorrido completo de una operacion y los cambios de la " +
      "retroalimentacion. Alexandy presenta los requisitos funcionales, los no funcionales y la seguridad. " +
      "El repositorio es publico y el codigo esta abierto en el editor. Gracias, quedamos atentos a las preguntas.";
  }

  const pptx = await PresentationFile.exportPptx(p);
  await pptx.save(SALIDA);

  for (const [indice, slide] of p.slides.items.entries()) {
    const png = await p.export({ slide, format: "png", scale: 1 });
    const nombre = `slide-${String(indice + 1).padStart(2, "0")}.png`;
    await fs.writeFile(path.join(SALIDA_PNG, nombre), new Uint8Array(await png.arrayBuffer()));
  }
  console.log(`Generado: ${SALIDA}`);
  console.log(`Miniaturas: ${SALIDA_PNG}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
