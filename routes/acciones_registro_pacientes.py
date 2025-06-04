# ╔═══════════════════════════════════════════════════════════════════╗
# ║     REGISTRO DE PACIENTES - ENDPOINTS BACKEND FASTAPI - MEDSYS   ║
# ╚═══════════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase, subir_pdf
from utils.email_sender import enviar_email_con_pdf
# Importamos la función de utilidades con un alias para evitar
# colisiones con el nombre del endpoint local.
from utils.pdf_generator import generar_pdf_registro_paciente as generar_pdf_registro_util
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "registro-pacientes"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_registro_paciente")
async def guardar_registro_paciente(
    request: Request,
    nombres: str = Form(...),
    apellido: str = Form(...),
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
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        data = {
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
            "usuario_id": usuario,
            "institucion_id": int(institucion_id)
        }

        supabase.table("registro_pacientes").insert(data).execute()
        return {"message": "Guardado exitosamente"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔════════════════════════════════════════════════════╗
# ║     GENERAR Y GUARDAR PDF REGISTRO DE PACIENTE     ║
# ╚════════════════════════════════════════════════════╝
@router.post("/generar_pdf_registro_paciente")
async def generar_pdf_registro_paciente(
    nombres: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...)
):
    try:
        datos = {
            "nombre_completo": f"{nombres} {apellido}".strip(),
            "dni": dni
        }

        # Usamos la función de utilidades para crear el PDF.
        pdf_path = generar_pdf_registro_util(datos)
        nombre_pdf = f"{dni}_registro_paciente.pdf"

        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        supabase.table("registro_pacientes").update({"pdf_url": pdf_url}).eq("dni", dni).execute()
        return {"pdf_url": pdf_url}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔═══════════════════════════════════════════════════╗
# ║     ENVIAR REGISTRO DE PACIENTE POR CORREO        ║
# ╚═══════════════════════════════════════════════════╝
@router.post("/enviar_pdf_registro_paciente")
async def enviar_pdf_registro_paciente(
    nombres: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        paciente = supabase.table("registro_pacientes").select("email").eq("dni", dni).single().execute()
        email = paciente.data.get("email") if paciente.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este paciente."}, status_code=404)
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        asunto = "Registro de Paciente - PDF"
        cuerpo = f"Estimado/a {nombres} {apellido}, adjuntamos su registro en formato PDF."

        enviar_email_con_pdf(email_destino=email, asunto=asunto, cuerpo=cuerpo, url_pdf=pdf_url)
        return {"message": "Correo enviado correctamente"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
