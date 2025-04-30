from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fpdf import FPDF
import sqlite3
import os
from respaldo.backup_handler import guardar_respaldo_completo

router = APIRouter()

DB_PATH = "static/doc/medsys.db"

@router.post("/eliminar-paciente")
async def eliminar_paciente(dni: str = Form(...), usuario: str = Form(...)):
    # Guardar respaldo antes de eliminar
    respaldo_exitoso = guardar_respaldo_completo(dni_paciente=dni, eliminado_por=usuario)

    if respaldo_exitoso:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Eliminar datos relacionados
        cursor.execute("DELETE FROM recetas WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM indicaciones WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM estudios WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM historia_clinica WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM turnos WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        
        # Finalmente, eliminar paciente
        cursor.execute("DELETE FROM pacientes WHERE dni=?", (dni,))
        
        conn.commit()
        conn.close()
        return RedirectResponse(url="/registro", status_code=303)
    else:
        return {"error": "Paciente no encontrado o respaldo fallido"}

@router.post("/generar_pdf_paciente")
async def generar_pdf_paciente(
    nombre: str = Form(...),
    dni: str = Form(...),
    fecha_nacimiento: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    domicilio: str = Form(...),
    obra_social: str = Form(...),
    numero_afiliado: str = Form(...),
    contacto_emergencia: str = Form(...)
):
    pdf = FPDF()
    pdf.add_page()

    # ENCABEZADO PROFESIONAL
    logo_path = "static/icons/logo-medicis-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)

    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 10, txt="MEDSYS", ln=1, align="R")

    subtitulo = "Registro de Pacientes"
    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 10, txt=subtitulo, ln=1, align="R")

    pdf.set_draw_color(90, 90, 90)
    pdf.set_line_width(0.5)
    pdf.line(10, 30, 200, 30)
    pdf.ln(15)

    # CONTENIDO DEL PDF
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"Nombre y Apellido: {nombre}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {dni}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de Nacimiento: {fecha_nacimiento}", ln=True)
    pdf.cell(200, 10, txt=f"Teléfono: {telefono}", ln=True)
    pdf.cell(200, 10, txt=f"Correo Electrónico: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Domicilio: {domicilio}", ln=True)
    pdf.cell(200, 10, txt=f"Obra Social / Prepaga: {obra_social}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Afiliado: {numero_afiliado}", ln=True)
    pdf.cell(200, 10, txt=f"Contacto de Emergencia: {contacto_emergencia}", ln=True)

    # PIE DE PÁGINA
    pdf.set_draw_color(90, 90, 90)
    pdf.line(10, 265, 200, 265)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.set_y(-15)
    pdf.cell(0, 10, "Salud Inteligente Para Un Mundo Real", 0, 0, "C")

    # GUARDADO
    safe_name = nombre.strip().replace(" ", "_")
    filename = f"paciente_{safe_name}.pdf"
    output_path = os.path.join("static/doc", filename)
    pdf.output(output_path)

    return JSONResponse({"filename": filename})
