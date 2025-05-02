from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fpdf import FPDF
import sqlite3
import os

router = APIRouter()
DB_PATH = "static/doc/medsys.db"

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
    try:
        # Guardar en base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pacientes (
                nombre, dni, fecha_nacimiento, telefono, email,
                domicilio, obra_social, numero_afiliado, contacto_emergencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nombre, dni, fecha_nacimiento, telefono, email,
            domicilio, obra_social, numero_afiliado, contacto_emergencia
        ))
        conn.commit()
        conn.close()

        # Generar PDF
        pdf = FPDF(format="A4")
        pdf.add_page()

        logo_path = "static/icons/logo-medsys-gris.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=1, w=62.7)
        else:
            print("LOGO NO ENCONTRADO:", logo_path)

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
            ("TelÃ©fono", telefono),
            ("Correo ElectrÃ³nico", email),
            ("Domicilio", domicilio),
            ("Obra Social / Prepaga", obra_social),
            ("NÃºmero de Afiliado", numero_afiliado),
            ("Contacto de Emergencia", contacto_emergencia)
        ]
        for label, value in campos:
            pdf.cell(0, 10, f"{label}: {value}", ln=True)

        # Ruta de guardado
        safe_name = nombre.strip().replace(" ", "_")
        output_dir = "static/doc"
        output_path = os.path.join(output_dir, f"paciente_{safe_name}.pdf")

        # Confirmar que el directorio existe
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Guardar el PDF
        resultado = pdf.output(output_path)
        if not os.path.exists(output_path):
            raise Exception(f"No se pudo guardar el PDF en {output_path}")

        return RedirectResponse(url="/registro", status_code=303)

    except Exception as e:
        return HTMLResponse(f"<h2>ERROR al generar PDF:</h2><pre>{str(e)}</pre>", status_code=500)
