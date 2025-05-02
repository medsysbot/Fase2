from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fpdf import FPDF
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from respaldo.backup_handler import guardar_respaldo_completo
from pathlib import Path
from supabase import create_client

router = APIRouter()

# Conexión con Supabase
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyMDE0OTMsImV4cCI6MjA2MTc3NzQ5M30.rV_1sa8iM8s6eCD-5m_wViCgWpd0d2xRHA_zQxRabHU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- GENERAR PDF + GUARDAR EN SUPABASE ----------
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

        paciente = {
            "dni": dni,
            "nombres": nombres,
            "apellido": apellido,
            "fecha_nacimiento": fecha_nacimiento,
            "telefono": telefono,
            "email": email,
            "domicilio": domicilio,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
            "contacto_emergencia": contacto_emergencia,
            "institucion_id": 1
        }

        supabase.table("pacientes").upsert(paciente, on_conflict="dni").execute()

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
    cuerpo = f"Estimado/a {nombres} {apellido},\n\nAdjuntamos el PDF correspondiente a su registro de paciente.\n\nSaludos cordiales,\nEquipo MedSys"

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
