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
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Registro de Paciente", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nombre y Apellido: {nombre}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {dni}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de Nacimiento: {fecha_nacimiento}", ln=True)
    pdf.cell(200, 10, txt=f"Teléfono: {telefono}", ln=True)
    pdf.cell(200, 10, txt=f"Correo Electrónico: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Domicilio: {domicilio}", ln=True)
    pdf.cell(200, 10, txt=f"Obra Social / Prepaga: {obra_social}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Afiliado: {numero_afiliado}", ln=True)
    pdf.cell(200, 10, txt=f"Contacto de Emergencia: {contacto_emergencia}", ln=True)

    safe_name = nombre.strip().replace(" ", "_")
    filename = f"paciente_{safe_name}.pdf"
    output_path = os.path.join("static/doc", filename)
    pdf.output(output_path)

    return JSONResponse({"filename": filename})
