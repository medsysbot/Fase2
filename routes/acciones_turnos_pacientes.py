# ╔════════════════════════════════════════════════════╗
# ║  TURNOS PACIENTES - ENDPOINTS BACKEND FASTAPI     ║
# ╚════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase, subir_pdf
from utils.email_sender import enviar_email_con_pdf
from utils.pdf_generator import generar_pdf_turno_paciente
from utils.image_utils import descargar_imagen, guardar_imagen_temporal
import os

router = APIRouter()

BUCKET_PDFS = "turnos-pacientes"
BUCKET_FIRMAS = "firma-sello-usuarios"
TABLE_NAME = "turnos_pacientes"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_turno_paciente")
async def guardar_turno_paciente(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(""),
):
    try:
        usuario_id = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario_id:
            return JSONResponse(status_code=403, content={"error": "Sesión inválida"})

        data = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "usuario_id": usuario_id,
            "institucion_id": int(institucion_id),
        }
        supabase.table(TABLE_NAME).insert(data).execute()
        return {"exito": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"exito": False, "mensaje": str(e)})


# ╔════════════════════════════════════════════╗
# ║       GENERAR Y GUARDAR PDF DEL TURNO      ║
# ╚════════════════════════════════════════════╝
@router.post("/generar_pdf_turno_paciente")
async def generar_pdf_turno_paciente_route(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(""),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "institucion_id": int(institucion_id),
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
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        (
            supabase.table(TABLE_NAME)
            .update({"pdf_url": pdf_url})
            .eq("dni", dni)
            .eq("fecha", fecha)
            .eq("hora", hora)
            .execute()
        )
        return {"exito": True, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"exito": False, "mensaje": str(e)})


# ╔══════════════════════════════════════════════════╗
# ║         ENVIAR PDF DE TURNO POR CORREO           ║
# ╚══════════════════════════════════════════════════╝
@router.post("/enviar_pdf_turno_paciente")
async def enviar_pdf_turno_paciente(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form("")
):
    try:
        if not pdf_url:
            res = (
                supabase.table(TABLE_NAME)
                .select("pdf_url")
                .eq("dni", dni)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            pdf_url = res.data[0]["pdf_url"] if res.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        paciente = (
            supabase.table("registro_pacientes")
            .select("email")
            .eq("dni", dni)
            .single()
            .execute()
        )
        email = paciente.data.get("email") if paciente.data else None
        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Turno Médico Confirmado",
            cuerpo=f"Estimado/a {nombre}, adjuntamos el comprobante de su turno.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"exito": False, "mensaje": str(e)})
