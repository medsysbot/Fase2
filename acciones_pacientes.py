from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client

router = APIRouter()

# Configuración de Supabase
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
service_client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

BUCKET_PDFS = "pdfs"
BUCKET_BACKUPS = "backups"

# ---------- GUARDAR Y GENERAR PDF ----------
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
        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        local_path = os.path.join("static/doc", filename)
        Path("static/doc").mkdir(parents=True, exist_ok=True)

        # PDF
        pdf = FPDF()
        pdf.add_page()
        logo = "static/icons/logo-medsys-gris.png"
        if os.path.exists(logo):
            pdf.image(logo, x=10, y=8, w=60)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 40, "Registro de Pacientes – MEDSYS", ln=True, align="C")
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

        pdf.output(local_path)

        # Subida a Supabase
        with open(local_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(filename, f, {
                "content-type": "application/pdf", "upsert": True
            })

        # Guardar en tabla
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

        url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
        return JSONResponse({"filename": filename, "url": url_publica})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ENVÍO POR CORREO ----------
@router.post("/enviar_pdf_paciente")
async def enviar_pdf_paciente(
    email: str = Form(...),
    nombres: str = Form(...),
    apellido: str = Form(...)
):
    try:
        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"

        remitente = "medisys.bot@gmail.com"
        contrasena = "yeuaugaxmdvydcou"

        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = email
        mensaje["Subject"] = "Registro de Pacientes – MEDSYS"
        cuerpo = f"""Estimado/a {nombres} {apellido},

Adjuntamos el documento con sus datos registrados.

Puede visualizarlo en este enlace:
{url}

Saludos,
Sistema MedSys"""

        mensaje.attach(MIMEText(cuerpo, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remitente, contrasena)
            server.send_message(mensaje)

        return JSONResponse({"mensaje": "Correo enviado correctamente."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ELIMINAR CON BACKUP ----------
@router.post("/eliminar-paciente")
async def eliminar_paciente(request: Request):
    try:
        data = await request.json()
        dni = data.get("dni")

        paciente_data, error = service_client.table("pacientes").select("*").eq("dni", dni).single().execute()
        if error or not paciente_data.data:
            return JSONResponse({"error": "Paciente no encontrado"}, status_code=404)

        paciente = paciente_data.data
        safe_name = f"{paciente['nombres'].replace(' ', '_')}_{paciente['apellido'].replace(' ', '_')}"
        filename = f"backup_{safe_name}_{dni}.pdf"
        local_path = os.path.join("static/doc", filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Backup Completo del Paciente", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        for k, v in paciente.items():
            pdf.cell(0, 10, f"{k.capitalize()}: {v}", ln=True)
        pdf.output(local_path)

        with open(local_path, "rb") as f:
            service_client.storage.from_(BUCKET_BACKUPS).upload(filename, f, {
                "content-type": "application/pdf", "upsert": True
            })

        service_client.table("pacientes").delete().eq("dni", dni).execute()

        return JSONResponse({"message": f"Paciente eliminado y respaldado: {filename}"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
