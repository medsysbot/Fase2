# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - INDICACIONES MÉDICAS         ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_indicaciones
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

BUCKET_PDFS = "indicaciones-medicas"
BUCKET_FIRMAS = "firma-sello-usuarios"

@router.post("/generar_pdf_indicaciones")
async def generar_indicaciones(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    indicaciones: str = Form(...),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        datos = {
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "indicaciones": indicaciones,
        }

        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        if firma:
            contenido_firma = await firma.read()
            ext_firma = os.path.splitext(firma.filename)[1].lower()
            nombre_firma = f"{base_firma}{ext_firma}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_firma):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_firma,
                    contenido_firma,
                    {"x-upsert": "true"},
                )
        elif usuario and institucion_id is not None:
            contenido_firma, nombre_firma = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_firma
            )

        if sello:
            contenido_sello = await sello.read()
            ext_sello = os.path.splitext(sello.filename)[1].lower()
            nombre_sello = f"{base_sello}{ext_sello}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_sello):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_sello,
                    contenido_sello,
                    {"x-upsert": "true"},
                )
        elif usuario and institucion_id is not None:
            contenido_sello, nombre_sello = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_sello
            )

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = generar_pdf_indicaciones(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("indicaciones").insert({
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "indicaciones": indicaciones,
            "pdf_url": pdf_url,
            "institucion_id": institucion_id,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_indicaciones")
async def enviar_pdf_indicaciones(nombre: str = Form(...), dni: str = Form(...)):
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        registros = supabase.table("indicaciones").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]["pdf_url"] if registros.data else None
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
