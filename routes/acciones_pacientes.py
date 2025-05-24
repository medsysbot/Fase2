from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
import os
from supabase import create_client, Client
from fpdf import FPDF
from utils.pdf_generator import generar_pdf_paciente
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "pdfs"
BUCKET_BACKUPS = "backups"

# ---------- REGISTRAR PACIENTE Y GENERAR PDF ----------
@router.post("/guardar_paciente")
async def guardar_paciente(
    request: Request,
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
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None:
            return JSONResponse({"error": "Sesión sin institución activa"}, status_code=403)

        existe = supabase.table("pacientes").select("dni").eq("dni", dni).eq("institucion_id", institucion_id).execute()
        if existe.data:
            return JSONResponse({"mensaje": "El paciente ya está registrado."}, status_code=200)
        datos = {
            "nombres": nombres,
            "apellido": apellido,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "telefono": telefono,
            "email": email,
            "domicilio": domicilio,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
            "contacto_emergencia": contacto_emergencia,
        }
        pdf_path = generar_pdf_paciente(datos)
        filename = os.path.basename(pdf_path)

        # Subir a Supabase
        with open(pdf_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(
                filename,
                file_data,
                {"content-type": "application/pdf"}
            )

        # Guardar en base
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

# ---------- ENVIAR PDF POR EMAIL ----------
@router.post("/enviar_pdf_paciente")
async def enviar_pdf_paciente(email: str = Form(...), nombres: str = Form(...), apellido: str = Form(...)):
    try:
        safe_name = f"{nombres.strip().replace(' ', '_')}_{apellido.strip().replace(' ', '_')}"
        filename = f"paciente_{safe_name}.pdf"
        pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Registro de Pacientes - MEDSYS",
            cuerpo=f"Estimado/a {nombres} {apellido},\n\nAdjuntamos su registro en PDF.\n\nSaludos,\nEquipo MEDSYS",
            url_pdf=pdf_url
        )      

        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ELIMINAR PACIENTE CON BACKUP ----------
@router.post("/eliminar_paciente")
async def eliminar_paciente(request: Request):
    try:
        datos = await request.json()
        dni = datos.get("dni")
        institucion_id = request.session.get("institucion_id")
        if not dni or not institucion_id:
            return JSONResponse({"error": "Faltan datos necesarios"}, status_code=400)

        # Buscar paciente
        paciente = supabase.table("pacientes").select("*").eq("dni", dni).eq("institucion_id", institucion_id).single().execute()
        if not paciente.data:
            return JSONResponse({"error": "Paciente no encontrado"}, status_code=404)

        datos_paciente = paciente.data

        # Generar PDF de backup
        safe_name = f"{datos_paciente['nombres'].replace(' ', '_')}_{datos_paciente['apellido'].replace(' ', '_')}"
        backup_name = f"backup_{safe_name}_{dni}.pdf"
        backup_path = os.path.join("static/doc", backup_name)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Backup del Paciente", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        for key, value in datos_paciente.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)

        pdf.output(backup_path)

        # Subir backup
        with open(backup_path, "rb") as f:
            supabase.storage.from_(BUCKET_BACKUPS).upload(backup_name, f)

        # Eliminar paciente
        supabase.table("pacientes").delete().eq("dni", dni).eq("institucion_id", institucion_id).execute()

        return JSONResponse({"exito": True, "mensaje": f"Paciente eliminado y respaldado como {backup_name}"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
