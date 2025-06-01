from fpdf import FPDF
import os
import datetime

# Ancho en milímetros para las imágenes de firma y sello
FIRMA_SELLO_ANCHO = 25


def _agregar_encabezado(pdf: FPDF, titulo: str) -> None:
    """Agrega el logo y el título con formato estándar en el PDF."""
    logo_path = "static/icons/logo-medsys-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=4, w=60)
    pdf.set_font("Arial", "B", 16)
    pdf.set_title(titulo)
    pdf.cell(0, 40, f"{titulo} - MEDSYS", ln=True, align="C")
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(1)
    pdf.line(10, 50, 200, 50)
    pdf.set_font("Arial", size=12)
    pdf.ln(15)

def generar_pdf_resumen(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Historia Clínica Resumida")

    pdf.cell(200, 10, txt=f"Paciente: {datos['paciente']}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {datos['dni']}", ln=True)
    pdf.cell(200, 10, txt=f"Edad: {datos['edad']}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Motivo de consulta:\n{datos['motivo']}\n")
    pdf.multi_cell(0, 10, f"Diagnóstico:\n{datos['diagnostico']}\n")
    pdf.multi_cell(0, 10, f"Tratamiento:\n{datos['tratamiento']}\n")
    pdf.multi_cell(0, 10, f"Observaciones:\n{datos['observaciones']}\n")

    if firma_path and os.path.exists(firma_path):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    filename = f"{datos['dni']}_resumen.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path

def generar_pdf_paciente(datos):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Registro de Pacientes")

    campos = [
        ("Nombre y Apellido", f"{datos['nombres']} {datos['apellido']}") ,
        ("DNI", datos["dni"]),
        ("Fecha de Nacimiento", datos["fecha_nacimiento"]),
        ("Teléfono", datos.get("telefono", "")),
        ("Correo Electrónico", datos.get("email", "")),
        ("Domicilio", datos.get("domicilio", "")),
        ("Obra Social / Prepaga", datos.get("obra_social", "")),
        ("Número de Afiliado", datos.get("numero_afiliado", "")),
        ("Contacto de Emergencia", datos.get("contacto_emergencia", "")),
    ]

    for label, value in campos:
        pdf.cell(0, 10, f"{label}: {value}", ln=True)

    safe_name = f"{datos['nombres'].strip().replace(' ', '_')}_{datos['apellido'].strip().replace(' ', '_')}"
    filename = f"paciente_{safe_name}.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path


def generar_pdf_historia_completa(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    logo_path = "static/icons/logo-medsys-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=4, w=60)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 40, "Historia Clínica Completa - MEDSYS", ln=True, align="C")
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(1)
    pdf.line(10, 50, 200, 50)
    pdf.set_font("Arial", size=12)
    pdf.ln(15)
    pdf.cell(0, 10, f"Paciente: {datos['nombre_completo']}", ln=True)

    campos = [
        ("DNI", datos["dni"]),
        ("Fecha de Nacimiento", datos["fecha_nacimiento"]),
        ("Edad", datos["edad"]),
        ("Sexo", datos["sexo"]),
        ("Teléfono", datos.get("telefono", "")),
        ("Correo Electrónico", datos.get("email", "")),
        ("Domicilio", datos.get("domicilio", "")),
        ("Obra Social / Prepaga", datos.get("obra_social", "")),
        ("Número de Afiliado", datos.get("numero_afiliado", "")),
        ("Antecedentes Personales", datos.get("antecedentes_personales", "")),
        ("Antecedentes Familiares", datos.get("antecedentes_familiares", "")),
        ("Hábitos", datos.get("habitos", "")),
        ("Enfermedades Crónicas", datos.get("enfermedades_cronicas", "")),
        ("Cirugías / Hospitalizaciones", datos.get("cirugias", "")),
        ("Medicación Actual", datos.get("medicacion", "")),
        ("Estudios Complementarios", datos.get("estudios", "")),
        ("Historial de Tratamientos", datos.get("historial_tratamientos", "")),
        ("Historial de Consultas", datos.get("historial_consultas", "")),
    ]

    for label, value in campos:
        pdf.cell(0, 10, f"{label}: {value}", ln=True)

    if firma_path and os.path.exists(firma_path):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    safe_name = datos["nombre_completo"].strip().replace(" ", "_")
    filename = f"historia_completa_{safe_name}_{datos['dni']}.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path

def _img_type_from_name(name: str) -> str:
    """Devuelve el tipo de imagen que espera FPDF a partir de su extensión."""
    ext = os.path.splitext(name.split("?")[0])[1].lower()
    if ext in (".jpg", ".jpeg"):
        return "JPG"
    if ext == ".png":
        return "PNG"
    return ""


def _es_url(path: str) -> bool:
    return path.startswith("http://") or path.startswith("https://")


def generar_pdf_recetas_medicas(datos, firma=None, sello=None):
    """Genera el PDF de la receta utilizando rutas locales o URLs de imagen."""
    pdf = FPDF()
    pdf.add_page()
    logo_path = "static/icons/logo-medsys-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=4, w=60)
    pdf.set_font("Arial", "B", 16)
    pdf.set_title("Receta Médica")
    pdf.cell(0, 40, txt="Receta Médica - MEDSYS", ln=True, align="C")
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(1)
    pdf.line(10, 50, 200, 50)
    pdf.set_font("Arial", size=12)
    pdf.ln(15)

    pdf.cell(0, 10, f"Paciente: {datos['nombre_completo']}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos['dni']}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datos['fecha']}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Diagnóstico:\n{datos['diagnostico']}\n")
    pdf.multi_cell(0, 10, f"Medicamentos indicados:\n{datos['medicamentos']}\n")

    if firma and (_es_url(firma) or os.path.exists(firma)):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        y_firma = pdf.get_y()
        pdf.image(firma, x=10, y=y_firma, w=FIRMA_SELLO_ANCHO, type=_img_type_from_name(firma))
        pdf.ln(FIRMA_SELLO_ANCHO + 5)

    if sello and (_es_url(sello) or os.path.exists(sello)):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        y_sello = pdf.get_y()
        pdf.image(sello, x=10, y=y_sello, w=FIRMA_SELLO_ANCHO, type=_img_type_from_name(sello))
        pdf.ln(FIRMA_SELLO_ANCHO + 5)

    filename = f"{datos['dni']}_recetas_medicas.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path


def generar_pdf_indicaciones_medicas(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Indicaciones Médicas")

    pdf.cell(0, 10, f"Paciente: {datos['nombre']}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos['dni']}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datos['fecha']}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Diagnóstico:\n{datos['diagnostico']}\n")
    pdf.multi_cell(0, 10, f"Indicaciones:\n{datos['indicaciones']}\n")

    if firma_path and os.path.exists(firma_path):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    filename = f"{datos['dni']}_indicaciones_medicas.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path


def generar_pdf_consulta_diaria(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Consulta Diaria")

    pdf.cell(0, 10, f"Paciente: {datos['paciente']}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos['dni']}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datos['fecha']}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Diagnóstico:\n{datos['diagnostico']}\n")
    pdf.multi_cell(0, 10, f"Evolución:\n{datos['evolucion']}\n")
    pdf.multi_cell(0, 10, f"Indicaciones:\n{datos['indicaciones']}\n")

    if datos.get("firma_url"):
        pdf.image(datos["firma_url"], x=160, y=240, w=30)
    elif firma_path and os.path.exists(firma_path):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    if datos.get("sello_url"):
        pdf.image(datos["sello_url"], x=20, y=240, w=30)
    elif sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=FIRMA_SELLO_ANCHO)
        pdf.ln(25)

    filename = f"{datos['dni']}_consulta_diaria.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path


def generar_pdf_turno(datos):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Turno Médico")

    fecha = datos.get('fecha')
    try:
        fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        fecha = fecha_obj.strftime("%d/%m/%Y")
    except Exception:
        pass

    campos = [
        ("Paciente", datos['nombre']),
        ("DNI", datos['dni']),
        ("Especialidad", datos.get('especialidad', '')),
        ("Fecha", fecha),
        ("Horario", datos['horario']),
        ("Profesional", datos.get('profesional', '')),
    ]
    for label, value in campos:
        pdf.cell(0, 10, f"{label}: {value}", ln=True)

    filename = f"{datos['dni']}_turno.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path


def generar_pdf_busqueda(datos):
    pdf = FPDF()
    pdf.add_page()
    _agregar_encabezado(pdf, "Resultado de Búsqueda")

    for key, value in datos.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)

    filename = f"{datos.get('dni', 'busqueda')}.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path
