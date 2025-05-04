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

# Configuración de Supabase
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY_SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjIwMTQ5MywiZXhwIjoyMDYxNzc3NDkzfQ.GJtQkyj4PBLxekNQXJq7-mqnnqpcb_Gp0O0nmpLxICM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY_SERVICE)

# Buckets definidos para los PDF y backups
BUCKET_PDFS = "pdfs"
BUCKET_BACKUPS = "backups"

# Ruta: Genera PDF, guarda en Supabase, guarda en la base de datos
@router.post("/generar_pdf_paciente")
async def generar_pdf(
    nombres: str = Form(...), apellido: str = Form(...), dni: str = Form(...),
    fecha_nacimiento: str = Form(...), telefono: str = Form(""), email: str = Form(""),
    domicilio: str = Form(""), obra_social: str = Form(""), numero_afiliado: str = Form(""),
    contacto_emergencia: str = Form("")
):
    try:
        # Verificar si el paciente ya está registrado
        existe = supabase.table("pacientes").select("dni").eq("dni", dni).execute()
        if existe.data:
            return JSONResponse({"mensaje": "El paciente ya está registrado."}, status_code=200)

        # Nombre seguro del archivo
        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        local_path = os.path.join("static/doc", filename)
        Path("static/doc").mkdir(parents=True, exist_ok=True)

        # Generar el PDF
        pdf = FPDF()
        pdf.add_page()

        # Encabezado
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

        # Cuerpo del PDF
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

        # Subir PDF a Supabase
        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(
                filename, file_data, {"content-type": "application/pdf"}
            )

        # Guardar datos del paciente
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
            "institucion_id": 1  # Fijo para pruebas iniciales
        }).execute()

        # Devolver URL pública
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
        return JSONResponse({"filename": filename, "url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Ruta: Envía PDF por correo al paciente
@router.post("/enviar_pdf_paciente")
async def enviar_pdf(email: str = Form(...), nombres: str = Form(...), apellido: str = Form(...)):
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

        return JSONResponse({"mensaje": "Correo enviado exitosamente"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Ruta: Elimina paciente y genera backup PDF
@router.post("/eliminar-paciente")
async def eliminar_paciente(request: Request):
    try:
        data = await request.json()
        dni = data.get("dni")

        # Buscar paciente por DNI
        paciente_data = supabase.table("pacientes").select("*").eq("dni", dni).single().execute()
        if not paciente_data.data:
            return JSONResponse({"error": "Paciente no encontrado"}, status_code=404)

        paciente = paciente_data.data
        safe_name = f"{paciente['nombres'].replace(' ', '_')}_{paciente['apellido'].replace(' ', '_')}"
        filename = f"backup_{safe_name}_{dni}.pdf"
        local_path = os.path.join("static/doc", filename)

        # Generar PDF de respaldo
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Backup Completo del Paciente", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        for key, value in paciente.items():
            pdf.cell(0, 10, f"{key.capitalize()}: {value}", ln=True)
        pdf.output(local_path)

        # Subir backup a Supabase
        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_BACKUPS).upload(filename, file_data)

        # Borrar de la base
        supabase.table("pacientes").delete().eq("dni", dni).execute()

        return JSONResponse({"message": f"Paciente eliminado y respaldado: {filename}"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
