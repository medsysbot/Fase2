from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from supabase import create_client

router = APIRouter()

# Supabase config
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY_SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
supabase = create_client(SUPABASE_URL, SUPABASE_KEY_SERVICE)

BUCKET_PDFS = "pdfs"
BUCKET_BACKUPS = "backups"

# REGISTRO + PDF
@router.post("/generar_pdf_paciente")
async def generar_pdf_paciente(
    request: Request,
    nombres: str = Form(...), apellido: str = Form(...), dni: str = Form(...),
    fecha_nacimiento: str = Form(...), telefono: str = Form(""), email: str = Form(""),
    domicilio: str = Form(""), obra_social: str = Form(""), numero_afiliado: str = Form(""),
    contacto_emergencia: str = Form("")
):
    try:
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None:
            return JSONResponse({"error": "No se encontró la institución en sesión"}, status_code=403)

        existe = supabase.table("pacientes").select("dni").eq("dni", dni).eq("institucion_id", institucion_id).execute()
        if existe.data:
            return JSONResponse({"mensaje": "El paciente ya está registrado."}, status_code=200)

        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        local_path = os.path.join("static/doc", filename)
        Path("static/doc").mkdir(parents=True, exist_ok=True)

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
                filename, file_data, {"content-type": "application/pdf"}
            )

        supabase.table("pacientes").insert({
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
            "institucion_id": institucion_id
        }).execute()

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
        return JSONResponse({"exito": True, "pdf_url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ENVÍO POR CORREO
@router.post("/enviar_pdf_paciente")
async def enviar_pdf_paciente(email: str = Form(...), nombres: str = Form(...), apellido: str = Form(...)):
    try:
        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        local_path = os.path.join("static/doc", filename)

        remitente = "medisys.bot@gmail.com"
        contrasena = "yeuaugaxmdvydcou"
        asunto = "Registro de Pacientes - MEDSYS"
        cuerpo = f"""Estimado/a {nombres} {apellido},\n\nAdjuntamos el PDF correspondiente a su registro de paciente.\n\nSaludos cordiales,\nEquipo MEDSYS"""

        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = email
        mensaje["Subject"] = asunto
        mensaje.attach(MIMEText(cuerpo, "plain"))

        with open(local_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            mensaje.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, contrasena)
            servidor.send_message(mensaje)

        return JSONResponse({"exito": True})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ELIMINAR PACIENTE + BACKUP
@router.post("/eliminar_paciente")
async def eliminar_paciente(request: Request):
    try:
        data = await request.json()
        dni = data.get("dni")
        institucion_id = request.session.get("institucion_id")
        if not institucion_id:
            return JSONResponse({"error": "Sesión inválida"}, status_code=403)

        paciente_data = supabase.table("pacientes").select("*").eq("dni", dni).eq("institucion_id", institucion_id).single().execute()
        if not paciente_data.data:
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
        for key, value in paciente.items():
            pdf.cell(0, 10, f"{key.capitalize()}: {value}", ln=True)
        pdf.output(local_path)

        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_BACKUPS).upload(filename, file_data)

        supabase.table("pacientes").delete().eq("dni", dni).eq("institucion_id", institucion_id).execute()

        return JSONResponse({"exito": True, "mensaje": f"Paciente eliminado y respaldado: {filename}"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
