from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
from supabase import create_client

router = APIRouter()

# Supabase config
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyMDE0OTMsImV4cCI6MjA2MTc3NzQ5M30.rV_1sa8iM8s6eCD-5m_wViCgWpd0d2xRHA_zQxRabHU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "pdfs"
BUCKET_BACKUPS = "backups"

# ---------- GENERAR PDF Y SUBIR A SUPABASE ----------
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

        pdf = FPDF()
        pdf.add_page()
        logo_path = "static/icons/logo-medsys-gris.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=60)
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

        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(
                filename, file_data, {"content-type": "application/pdf", "upsert": True}
            )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"

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

        return JSONResponse({"filename": filename, "url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ENVIAR PDF POR EMAIL ----------
@router.post("/enviar_pdf_paciente")
async def enviar_pdf_paciente(email: str = Form(...), nombres: str = Form(...), apellido: str = Form(...)):
    from smtplib import SMTP_SSL
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
    filename = f"paciente_{safe_name}.pdf"
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"

    remitente = "medisys.bot@gmail.com"
    contrasena = "yeuaugaxmdvydcou"
    asunto = "Registro de Pacientes – MEDSYS"
    cuerpo = f"Estimado/a {nombres} {apellido},\n\nAdjuntamos el PDF de su registro:\n{public_url}\n\nSaludos,\nMedSys"

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = email
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        with SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, contrasena)
            servidor.send_message(mensaje)
        return JSONResponse({"mensaje": "Correo enviado exitosamente"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ELIMINAR PACIENTE CON RESPALDO EN PDF ----------
@router.post("/eliminar-paciente")
async def eliminar_paciente(data: dict):
    dni = data.get("dni")
    paciente_data, error = supabase.table("pacientes").select("*").eq("dni", dni).single().execute()

    if error or not paciente_data.data:
        return JSONResponse({"error": "Paciente no encontrado"}, status_code=404)

    paciente = paciente_data.data
    safe_name = f"{paciente['nombres'].replace(' ', '_')}_{paciente['apellido'].replace(' ', '_')}"
    backup_filename = f"backup_{safe_name}_{dni}.pdf"
    backup_local_path = os.path.join("static/doc", backup_filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Backup Completo del Paciente", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for key, value in paciente.items():
        pdf.cell(0, 10, f"{key.capitalize()}: {value}", ln=True)
    pdf.output(backup_local_path)

    with open(backup_local_path, "rb") as file_data:
        supabase.storage.from_(BUCKET_BACKUPS).upload(
            backup_filename, file_data, {"content-type": "application/pdf", "upsert": True}
        )

    supabase.table("pacientes").delete().eq("dni", dni).execute()

    return JSONResponse({"message": f"Paciente eliminado y respaldado: {backup_filename}"})
