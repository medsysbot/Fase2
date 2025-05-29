# ╔════════════════════════════════════╗
# ║       ACCIONES RECETA MÉDICA       ║
# ╚════════════════════════════════════╝

from fastapi import APIRouter, Form
from supabase import create_client
import os
from fpdf import FPDF
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

router = APIRouter()

# Configuración Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración correo
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False
)

# ╔════════════════════════════════════╗
# ║       GENERAR PDF DE RECETA        ║
# ╚════════════════════════════════════╝
@router.post("/generar_pdf_receta")
async def generar_pdf_receta(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    medicamentos: str = Form(...)
):
    try:
        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Receta Médica", ln=True, align='C')
        pdf.ln(10)
        contenido = (
            f"Paciente: {nombre} {apellido}\n"
            f"DNI: {dni}\n"
            f"Fecha: {fecha}\n\n"
            f"Diagnóstico:\n{diagnostico}\n\n"
            f"Medicamentos indicados:\n{medicamentos}"
        )
        pdf.multi_cell(0, 10, contenido)

        # Guardar PDF temporalmente
        pdf_filename = f"receta_{dni}.pdf"
        pdf_path = f"/tmp/{pdf_filename}"
        pdf.output(pdf_path)

        # Subir PDF a Supabase
        bucket_name = "recetas-medicas"
        with open(pdf_path, "rb") as pdf_file:
            supabase.storage.from_(bucket_name).upload(
                pdf_filename,
                pdf_file,
                {"content-type": "application/pdf", "upsert": True}
            )

        # Obtener URL pública del PDF
        pdf_url = supabase.storage.from_(bucket_name).get_public_url(pdf_filename)

        # Devolver URL al frontend
        return {"resultado": "ok", "pdf_url": pdf_url}

    except Exception as e:
        print(f"Error al generar o subir el PDF: {e}")
        return {"resultado": "error", "mensaje": str(e)}

# ╔════════════════════════════════════╗
# ║       ENVIAR PDF POR CORREO        ║
# ╚════════════════════════════════════╝
@router.post("/enviar_pdf_receta")
async def enviar_pdf_receta(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        # Obtener email desde Supabase
        email_result = supabase.table("pacientes").select("email").eq("dni", dni).execute().data
        if not email_result:
            return {"exito": False, "mensaje": "No se encontró email del paciente."}

        paciente_email = email_result[0]['email']

        # Preparar contenido del correo
        html_content = f"""
        <p>Hola {nombre},</p>
        <p>Puedes descargar tu receta médica en el siguiente enlace:</p>
        <p><a href="{pdf_url}">{pdf_url}</a></p>
        """

        # Enviar correo electrónico
        message = MessageSchema(
            subject="Receta Médica PDF",
            recipients=[paciente_email],
            body=html_content,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        return {"exito": True}

    except Exception as e:
        print(f"Error al enviar el email: {e}")
        return {"exito": False, "mensaje": str(e)}
