# ╔════════════════════════════════════════════════════════════╗
# ║           ACCIONES BACKEND - TURNOS MÉDICOS               ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
import os
from utils.pdf_generator import generar_pdf_turno_paciente as generar_pdf_turno_paciente_sync
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import (
    guardar_imagen_temporal,
    descargar_imagen,
)
from utils.supabase_helper import supabase, subir_pdf
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# ╔══════════════════════════════════════════════╗
# ║              CONFIGURACIÓN                   ║
# ╚══════════════════════════════════════════════╝
BUCKET_PDFS = "turnos_pacientes"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔══════════════════════════════════════════════╗
# ║          GENERAR Y GUARDAR TURNO             ║
# ╚══════════════════════════════════════════════╝
@router.post("/generar_pdf_turno_paciente")
async def generar_pdf_turno_paciente(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form("")
):
    try:
        usuario_id = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario_id:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        # Validar campos requeridos
        campos_requeridos = [
            dni,
            nombre,
            apellido,
            profesional,
            especialidad,
            fecha,
            hora,
            usuario_id,
            institucion_id,
        ]
        if not all(campos_requeridos):
            return JSONResponse({"error": "Faltan datos obligatorios"}, status_code=400)

        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "profesional": profesional,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
        }

        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"

        firma_path = sello_path = None

        contenido_firma, nombre_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        contenido_sello, nombre_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)
        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = generar_pdf_turno_paciente_sync(datos, firma_path, sello_path)
        filename = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as file_data:
            public_url = subir_pdf(BUCKET_PDFS, filename, file_data)

        if not public_url:
            return JSONResponse({"error": "No se pudo obtener URL del PDF"}, status_code=500)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("turnos_pacientes").insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "pdf_url": public_url,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ╔══════════════════════════════════════════════╗
# ║         ENVIAR PDF POR EMAIL (OPCIONAL)      ║
# ╚══════════════════════════════════════════════╝
@router.post("/enviar_pdf_turno_paciente")
async def enviar_pdf_turno_paciente(
    email: str = Form(...),
    nombre: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        cuerpo = (
            f"Hola {nombre},\n\nAdjuntamos el comprobante de su turno médico.\n\n"
            f"Gracias por usar MEDSYS."
        )
        enviar_email_con_pdf(
            email_destino=email,
            asunto="Turno Médico - MEDSYS",
            cuerpo=cuerpo,
            url_pdf=pdf_url
        )
        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
