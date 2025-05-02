from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
from supabase import create_client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

# Supabase config
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Registro de Pacientes - MEDSYS", ln=True, align="C")
        pdf.set_draw_color(0, 120, 215)
        pdf.set_line_width(1)
        pdf.line(10, 20, 200, 20)
        pdf.set_font("Arial", size=12)
        pdf.ln(10)

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
            pdf.cell(0, 10, f"{label}: {value}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

        pdf.output(local_path)

        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(
                filename, file_data, {"content-type": "application/pdf", "upsert": True}
            )

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

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"

        return JSONResponse({"filename": filename, "url": public_url})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ELIMINAR PACIENTE CON RESPALDO PDF ----------
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
    pdf.cell(0, 10, "Backup del Paciente", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    for key, value in paciente.items():
        pdf.cell(0, 10, f"{key}: {str(value)}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.output(backup_local_path)

    with open(backup_local_path, "rb") as file_data:
        supabase.storage.from_(BUCKET_BACKUPS).upload(
            backup_filename, file_data, {"content-type": "application/pdf", "upsert": True}
        )

    supabase.table("pacientes").delete().eq("dni", dni).execute()

    return JSONResponse({"message": f"Paciente eliminado y respaldado: {backup_filename}"})
