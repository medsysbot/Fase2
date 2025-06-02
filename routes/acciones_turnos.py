# ╔════════════════════════════════════════════════╗
# ║          RUTA BACKEND - TURNOS PACIENTES      ║
# ╚════════════════════════════════════════════════╝

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse
from utils import (
    generar_pdf_turno_paciente,
    enviar_email_con_pdf,
)
from utils.supabase_helper import supabase, subir_pdf_a_bucket
import tempfile

router = APIRouter()

@router.post("/generar_pdf_turno_paciente")
async def generar_turno_paciente(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(""),
    institucion_id: int = Form(...),
    usuario_id: str = Form(...)
):
    try:
        # ═════ Validar sesión ═════
        if not institucion_id or not usuario_id:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        # ═════ Validación de campos ═════
        campos = [dni, nombre, apellido, especialidad, profesional, fecha, hora, usuario_id, institucion_id]
        if not all(c and str(c).strip() != "" for c in campos):
            return JSONResponse({"exito": False, "mensaje": "Faltan campos obligatorios."})

        # ═════ Generar PDF temporal ═════
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = temp_file.name
        generar_pdf_turno_paciente(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            especialidad=especialidad,
            profesional=profesional,
            fecha=fecha,
            hora=hora,
            observaciones=observaciones,
            output_path=pdf_path
        )

        # ═════ Subir a Supabase ═════
        nombre_archivo = f"{dni}_{fecha}_{hora}.pdf".replace(" ", "_").replace(":", "-")
        url_pdf = subir_pdf_a_bucket(
            bucket="turnos_pacientes",
            archivo_path=pdf_path,
            nombre_archivo=nombre_archivo,
            carpeta=f"{dni}"
        )

        # ═════ Insertar en Supabase DB ═════
        supabase.table("turnos_pacientes").insert({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "pdf_url": url_pdf,
            "usuario_id": usuario_id,
            "institucion_id": institucion_id
        }).execute()

        return {"exito": True, "pdf_url": url_pdf}

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": f"Error al generar turno: {str(e)}"})

@router.post("/enviar_pdf_turno_paciente")
async def enviar_turno_paciente_por_email(
    email: str = Form(...),
    nombre: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        asunto = "Confirmación de turno médico"
        cuerpo = f"Estimado/a {nombre},\n\nAdjuntamos el PDF con los detalles de su turno médico.\n\nSaludos,\nEquipo MedSys"
        exito = enviar_email_con_pdf(email_destino=email, asunto=asunto, cuerpo=cuerpo, pdf_url=pdf_url)

        if exito:
            return {"exito": True}
        else:
            return {"exito": False, "mensaje": "No se pudo enviar el correo"}

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": f"Error al enviar el email: {str(e)}"})
