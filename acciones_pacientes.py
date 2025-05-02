from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fpdf import FPDF
import sqlite3
import os
from respaldo.backup_handler import guardar_respaldo_completo

router = APIRouter()
DB_PATH = "static/doc/medsys.db"

# ---------- ELIMINAR PACIENTE ----------
@router.post("/eliminar-paciente")
async def eliminar_paciente(dni: str = Form(...), usuario: str = Form(...)):
    respaldo_exitoso = guardar_respaldo_completo(dni_paciente=dni, eliminado_por=usuario)
    if respaldo_exitoso:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for tabla in ["recetas", "indicaciones", "estudios", "historia_clinica", "turnos"]:
            cursor.execute(f"DELETE FROM {tabla} WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM pacientes WHERE dni=?", (dni,))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/registro", status_code=303)
    else:
        return {"error": "Paciente no encontrado o respaldo fallido"}

# ---------- GUARDAR PACIENTE Y GENERAR PDF ----------
@router.post("/generar_pdf_paciente")
async def generar_pdf_paciente(
    request: Request,
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
    # --- Guardar en base de datos ---
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pacientes (nombre, dni, fecha_nacimiento, telefono, email, domicilio, obra_social, numero_afiliado, contacto_emergencia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, dni, fecha_nacimiento, telefono, email, domicilio, obra_social, numero_afiliado, contacto_emergencia))
    conn.commit()
    conn.close()

    # --- Generar PDF ---
    pdf = FPDF(format="A4")
    pdf.add_page()

    logo_path = "static/icons/logo-medsys-gris.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=1, w=62.7)

    pdf.set_y(22)
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 10, txt="Registro de Pacientes", ln=True, align="C")

    pdf.set_draw_color(90, 90, 90)
    pdf.set_line_width(0.5)
    pdf.line(15, 47, 195, 47)
    pdf.ln(17)

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    campos = [
        ("Nombre y Apellido", nombre),
        ("DNI", dni),
        ("Fecha de Nacimiento", fecha_nacimiento),
        ("Teléfono", telefono),
        ("Correo Electrónico", email),
        ("Domicilio", domicilio),
        ("Obra Social / Prepaga", obra_social),
        ("Número de Afiliado", numero_afiliado),
        ("Contacto de Emergencia", contacto_emergencia)
    ]
    for label, value in campos:
        pdf.cell(0, 10, f"{label}: {value}", ln=True)

    safe_name = nombre.strip().replace(" ", "_")
    filename = f"paciente_{safe_name}.pdf"
    output_path = os.path.join("static/doc", filename)
    pdf.output(output_path)

    return RedirectResponse(url="/registro", status_code=303)
