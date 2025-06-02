from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_turno_paciente
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import guardar_imagen_temporal
from utils.supabase_helper import supabase
from datetime import datetime
import uuid

router = APIRouter()

# ╔════════════════════════════════════════════╗
# ║     GUARDAR TURNO Y GENERAR PDF (PÚBLICO) ║
# ╚════════════════════════════════════════════╝
@router.post("/generar_pdf_turno_paciente")
async def generar_turno_y_pdf(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    profesional: str = Form(...),
    usuario_id: str = Form(...),
    institucion_id: int = Form(...),
):
    try:
        # Validación mínima
        campos_obligatorios = [dni, fecha, hora, profesional, usuario_id, institucion_id]
        if not all(campos_obligatorios):
            return JSONResponse(content={"exito": False, "mensaje": "Faltan campos obligatorios"}, status_code=400)

        # Generar nombre único para PDF
        nombre_archivo = f"{dni}_{fecha}_{uuid.uuid4().hex[:8]}.pdf"

        # Generar PDF
        pdf_bytes = await generar_pdf_turno_paciente(nombre, apellido, dni, especialidad, fecha, hora, profesional)

        # Subir a Supabase
        bucket = "turnos_pacientes"
        supabase.storage.from_(bucket).upload(nombre_archivo, pdf_bytes, {"content-type": "application/pdf"})

        # Obtener URL pública
        pdf_url = f"https://{supabase.storage_url}/{bucket}/{nombre_archivo}"

        # Insertar en la tabla
        supabase.table("turnos_pacientes").insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "profesional": profesional,
            "usuario_id": usuario_id,
            "institucion_id": institucion_id,
            "pdf_url": pdf_url,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return JSONResponse(content={"exito": True, "pdf_url": pdf_url})

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

# ╔═════════════════════════════════════════════════╗
# ║       ENVIAR PDF DE TURNO POR CORREO           ║
# ╚═════════════════════════════════════════════════╝
@router.post("/enviar_pdf_turno_paciente")
async def enviar_pdf_turno(
    dni: str = Form(...),
    nombre: str = Form(...),
    email: str = Form(...),
):
    try:
        # Buscar el turno más reciente
        resultado = supabase.table("turnos_pacientes") \
            .select("pdf_url") \
            .eq("dni", dni) \
            .order("created_at", desc=True) \
            .limit(1).execute()

        if not resultado.data:
            return JSONResponse(content={"exito": False, "mensaje": "No se encontró el PDF"}, status_code=404)

        pdf_url = resultado.data[0]["pdf_url"]
        asunto = "Confirmación de turno médico"
        cuerpo = f"Estimado/a {nombre},\n\nAdjuntamos el comprobante de su turno médico.\n\nGracias por usar MedSys."

        await enviar_email_con_pdf(email, asunto, cuerpo, pdf_url)
        return JSONResponse(content={"exito": True})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
