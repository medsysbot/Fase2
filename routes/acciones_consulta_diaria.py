# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - EVOLUCIÓN DIARIA             ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
import logging
# La función para crear el PDF de la evolución diaria se renombró a
# `generar_pdf_consulta_diaria` en `utils/pdf_generator.py`. Actualizamos el
# import para usar el nombre correcto y evitar errores al iniciar la app.
from utils.pdf_generator import generar_pdf_consulta_diaria
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.image_utils import (
    guardar_imagen_temporal,
    descargar_imagen,
    imagen_existe,
)

from utils.supabase_helper import supabase, SUPABASE_URL, subir_pdf

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "evolucion-diaria"
BUCKET_FIRMAS = "firma-sello-usuarios"

@router.post("/generar_pdf_evolucion")
async def generar_evolucion(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    evolucion: str = Form(...),
    indicaciones: str = Form(...),
    paciente: str = Form(None),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        paciente = paciente or f"{nombre} {apellido}".strip()

        datos = {
            "paciente": paciente,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
        }

        firma_path = sello_path = None
        firma_url = sello_url = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        contenido_firma, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_firma
        )
        contenido_sello, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_sello
        )
        if nombre_firma:
            firma_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_FIRMAS}/{nombre_firma}"
        if nombre_sello:
            sello_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_FIRMAS}/{nombre_sello}"

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        datos["firma_url"] = firma_url
        datos["sello_url"] = sello_url

        # Generamos el PDF utilizando la función correcta del módulo
        # `pdf_generator`. Antes se llamaba `generar_pdf_evolucion`, pero el
        # nombre actual es `generar_pdf_consulta_diaria`.
        pdf_path = generar_pdf_consulta_diaria(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("evolucion_diaria").insert({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
            "institucion_id": institucion_id,
            "pdf_url": pdf_url,        
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        logging.error(f"Error al guardar evolución diaria: {e}")
        return JSONResponse(content={"exito": False, "mensaje": "Error al guardar la evolución"}, status_code=500)


@router.post("/obtener_email_evolucion")
async def obtener_email_evolucion(dni: str = Form(...)):
    """Devuelve el email del paciente a partir de su DNI."""
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None
        return {"email": email}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_evolucion")
async def enviar_pdf_evolucion(paciente: str = Form(...), dni: str = Form(...)):
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        registros = supabase.table("consultas").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]["pdf_url"] if registros.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Evolución Diaria",
            cuerpo=f"Estimado/a {paciente}, adjuntamos la evolución registrada.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
