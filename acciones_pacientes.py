from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fpdf import FPDF
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from respaldo.backup_handler import guardar_respaldo_completo
from pathlib import Path

router = APIRouter()
DB_PATH = "static/doc/medsys.db"

# ---------- GENERAR PDF + GUARDAR EN BASE ----------
@router.post("/generar_pdf_paciente")
async def generar_pdf_paciente(
    nombres: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha_nacimiento: str = Form(...),
    telefono: str = Form(""),
    email: str = Form(""),
    domicilio: str = Form(""),
    obra_social: str = Form(""),
    numero_afiliado: str = Form(""),
    contacto_emergencia: str = Form("")
):
    try:
        pdf = FPDF()
        pdf.add_page()

        logo_path = "static/icons/logo-medsys-gris.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=60)

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 40, "Registro de Pacientes", ln=True, align="C")

        pdf.set_draw_color(0, 120, 215)
        pdf.set_line_width(1)
        pdf.line(10, 50, 200, 50)

        pdf.set_font("Arial", size=12)
        pdf.ln(15)

        campos = [
            ("Nombre y Apellido", f"{nombres} {apellido}"),
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

        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        output_dir = "static/doc"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"paciente_{safe_name}.pdf"
        output_path = os.path.join(output_dir, filename)
        pdf.output(output_path)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO pacientes
            (dni, nombres, apellido, fecha_nacimiento, telefono, email, direccion, institucion_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            dni, nombres, apellido, fecha_nacimiento, telefono, email, domicilio
        ))
        conn.commit()
        conn.close()

        return JSONResponse({"filename": filename})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ENVIAR PDF POR EMAIL ----------
@router.post("/enviar_pdf_paciente")
async def enviar_pdf_paciente(email: str = Form(...), nombres: str = Form(...), apellido: str = Form(...)):
    safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
    filename = f"paciente_{safe_name}.pdf"
    filepath = os.path.join("static/doc", filename)

    if not os.path.exists(filepath):
        return JSONResponse({"error": "PDF no encontrado. Verifica que esté generado."}, status_code=404)

    remitente = "medisys.bot@gmail.com"
    contrasena = "yeuaugaxmdvydcou"
    asunto = "Registro de Pacientes – MEDSYS"
    cuerpo = f"""Estimado/a {nombres} {apellido},

Adjuntamos el PDF correspondiente a su registro de paciente.

Este documento contiene sus datos personales y será utilizado para futuras gestiones médicas.

Saludos cordiales,

Equipo MedSys"""

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = email
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    with open(filepath, "rb") as archivo_pdf:
        parte = MIMEApplication(archivo_pdf.read(), _subtype="pdf")
        parte.add_header("Content-Disposition", "attachment", filename=filename)
        mensaje.attach(parte)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, contrasena)
            servidor.send_message(mensaje)
        return JSONResponse({"mensaje": "Correo enviado exitosamente"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ELIMINAR PACIENTE CON RESPALDO ----------
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
        return JSONResponse({"error": "Paciente no encontrado o respaldo fallido"}, status_code=500)
