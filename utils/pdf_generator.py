from fpdf import FPDF
import os

def generar_pdf_resumen(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("Historia Clínica Resumida")

    pdf.cell(200, 10, txt="Historia Clínica Resumida", ln=True, align="C")
    pdf.ln(10)

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
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=40)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=40)
        pdf.ln(25)

    filename = f"{datos['dni']}_resumen.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    

def generar_pdf_paciente(datos):
    pdf = FPDF()
    pdf.add_page()
    logo_path = "static/icons/logo-medsys-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=4, w=60)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 40, "Registro de Pacientes - MEDSYS", ln=True, align="C")
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(1)
    pdf.line(10, 50, 200, 50)
    pdf.set_font("Arial", size=12)
    pdf.ln(15)

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

    campos = [
        ("Nombre del Paciente", datos["nombre"]),
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
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=40)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=40)
        pdf.ln(25)

    safe_name = datos["nombre"].strip().replace(" ", "_")
    filename = f"historia_completa_{safe_name}_{datos['dni']}.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path
