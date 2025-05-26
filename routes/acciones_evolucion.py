# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - EVOLUCIÓN DIARIA             ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from utils.pdf_generator import generar_pdf_evolucion
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.image_utils import (
    guardar_imagen_temporal,
    descargar_imagen,
    eliminar_imagen,
    ALLOWED_EXTENSIONS,
)

load_dotenv()
router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "evolucion-diaria"
BUCKET_FIRMAS = "firma-sello-usuarios"

@router.post("/generar_pdf_evolucion")
async def generar_evolucion(
    request: Request,
    paciente: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    evolucion: str = Form(...),
    indicaciones: str = Form(...),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        datos = {
            "paciente": paciente,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
        }

        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        if firma:
            contenido_firma = await firma.read()
            ext_firma = os.path.splitext(firma.filename)[1].lower()
            if ext_firma not in ALLOWED_EXTENSIONS:
                return JSONResponse(
                    {"exito": False, "mensaje": "Formato de imagen no soportado para firma o sello"},
                    status_code=400,
                )
            eliminar_imagen(supabase, BUCKET_FIRMAS, base_firma)
            nombre_firma = f"{base_firma}{ext_firma}"
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_firma,
                contenido_firma,
                {"content-type": firma.content_type},
                upsert=True,
            )
        elif usuario and institucion_id is not None:
            contenido_firma, nombre_firma = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_firma
            )

        if sello:
            contenido_sello = await sello.read()
            ext_sello = os.path.splitext(sello.filename)[1].lower()
            if ext_sello not in ALLOWED_EXTENSIONS:
                return JSONResponse(
                    {"exito": False, "mensaje": "Formato de imagen no soportado para firma o sello"},
                    status_code=400,
                )
            eliminar_imagen(supabase, BUCKET_FIRMAS, base_sello)
            nombre_sello = f"{base_sello}{ext_sello}"
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_sello,
                contenido_sello,
                {"content-type": sello.content_type},
                upsert=True,
            )
        elif usuario and institucion_id is not None:
            contenido_sello, nombre_sello = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_sello
            )

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = generar_pdf_evolucion(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(nombre_pdf, f, upsert=True)

        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_pdf)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("consultas").insert({
            "paciente": paciente,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
            "pdf_url": pdf_url,
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_evolucion")
async def enviar_pdf_evolucion(email: str = Form(...), paciente: str = Form(...), dni: str = Form(...)):
    try:
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
