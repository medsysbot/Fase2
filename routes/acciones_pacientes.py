# ╔══════════════════════════════════════════════════════════════════════╗
# ║              RUTAS - TURNOS PACIENTES (INTERNOS Y PÚBLICOS)         ║
# ╚══════════════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Request, Form, UploadFile
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase, subir_pdf
from utils.pdf_generator import generar_pdf_turno_paciente
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import descargar_imagen, guardar_imagen_temporal
import tempfile
from datetime import datetime
import os

router = APIRouter()

BUCKET_PDFS = "turnos-pacientes"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ════════════════════════════════════════════════════════════════════════
# 📌 ENDPOINT: Generar y guardar PDF de turno médico
# ════════════════════════════════════════════════════════════════════════
@router.post("/generar_pdf_turno_paciente")
async def generar_pdf_turno_paciente_route(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    profesional: str = Form(...)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        # Validaciones mínimas
        campos_obligatorios = [nombre, apellido, dni, especialidad, fecha, hora, profesional]
        if not all(campos_obligatorios):
            return JSONResponse({"exito": False, "mensaje": "Faltan campos obligatorios."}, status_code=400)

        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "profesional": profesional,
            "institucion_id": int(institucion_id)
        }

        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        c_firma, n_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        c_sello, n_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)
        if c_firma:
            firma_path = guardar_imagen_temporal(c_firma, n_firma)
        if c_sello:
            sello_path = guardar_imagen_temporal(c_sello, n_sello)

        pdf_path = generar_pdf_turno_paciente(datos, firma_path, sello_path)
        nombre_archivo = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as f:
            url_pdf = subir_pdf(BUCKET_PDFS, nombre_archivo, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        # Guardar registro en la tabla
        supabase.table("turnos_pacientes").insert([{
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "profesional": profesional,
            "usuario_id": usuario,
            "institucion_id": int(institucion_id),
            "pdf_url": url_pdf
        }]).execute()

        return JSONResponse({"exito": True, "pdf_url": url_pdf})

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

# ════════════════════════════════════════════════════════════════════════
# 📩 ENDPOINT: Enviar PDF por correo al paciente
# ════════════════════════════════════════════════════════════════════════
@router.post("/enviar_pdf_turno_paciente")
async def enviar_pdf_turno(
    nombre: str = Form(...),
    dni: str = Form(...),
    email: str = Form(...)
):
    try:
        # Buscar último PDF generado para el paciente
        resultado = supabase.table("turnos_pacientes") \
            .select("pdf_url") \
            .eq("dni", dni) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not resultado.data or not resultado.data[0].get("pdf_url"):
            return JSONResponse({"exito": False, "mensaje": "No se encontró PDF para este paciente"}, status_code=404)

        url_pdf = resultado.data[0]["pdf_url"]
        asunto = "Turno Médico Confirmado"
        cuerpo = f"Hola {nombre},\n\nAdjuntamos el comprobante de su turno médico.\n\nGracias por usar MedSys."
        enviado = enviar_email_con_pdf(email, asunto, cuerpo, url_pdf)

        if enviado:
            return JSONResponse({"exito": True})
        else:
            return JSONResponse({"exito": False, "mensaje": "No se pudo enviar el correo"}, status_code=500)

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

@router.post("/obtener_email_paciente")
async def obtener_email_paciente(dni: str = Form(...)):
    """Devuelve el email del paciente a partir de su DNI."""
    try:
        resultado = supabase.table("registro_pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None
        return {"email": email}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
