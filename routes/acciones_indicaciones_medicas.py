# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - INDICACIONES MÉDICAS         ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_indicaciones_medicas
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.image_utils import (
    descargar_imagen,
    eliminar_imagen,
    imagen_existe,
    guardar_imagen_temporal,
)

from utils.supabase_helper import supabase, subir_pdf

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "indicaciones-medicas"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO          ║
# ╚════════════════════════════════════╝
@router.post("/guardar_indicacion_medica")
async def guardar_indicacion_medica(
    request: Request,
    dni: str = Form(...),
    profesional: str = Form(...),
    indicacion: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        institucion_id = int(institucion_id)
        usuario_id = str(usuario)

        data = {
            "dni": dni,
            "profesional": profesional,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
            "indicaciones": indicacion,
        }
        supabase.table("indicaciones_medicas").insert(data).execute()
        return {"message": "Guardado exitosamente"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔══════════════════════════════════════╗
# ║   GENERAR Y GUARDAR PDF INDICACIÓN   ║
# ╚══════════════════════════════════════╝
@router.post("/generar_pdf_indicacion_medica")
async def generar_pdf_indicacion_medica(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    indicaciones: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        institucion_id = int(institucion_id)
        usuario_id = str(usuario)
        datos = {
            "nombre": f"{nombre} {apellido}".strip(),
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "indicaciones": indicaciones,
        }

        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        contenido_firma, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_firma
        )
        contenido_sello, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_sello
        )

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = generar_pdf_indicaciones_medicas(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("indicaciones_medicas").insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "indicaciones": indicaciones,
            "pdf_url": pdf_url,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


# ╔════════════════════════════════════════════╗
# ║   ENVIAR INDICACIÓN MÉDICA POR CORREO      ║
# ╚════════════════════════════════════════════╝
@router.post("/enviar_pdf_indicacion_medica")
async def enviar_pdf_indicacion_medica(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)
        enviar_email_con_pdf(
            email_destino=email,
            asunto="Indicaciones Médicas",
            cuerpo=f"Estimado/a {nombre}, adjuntamos sus indicaciones.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
