# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - INDICACIONES MÉDICAS         ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from utils.pdf_generator import generar_pdf_indicaciones
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os, tempfile

load_dotenv()
router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
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
        datos = {
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "indicaciones": indicaciones,
        }

        firma_path = sello_path = None
        if firma:
            contenido_firma = await firma.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                f"firma-{usuario}--{institucion_id}.png",
                contenido_firma,
                {"content-type": firma.content_type},
            )
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(contenido_firma)
            tmp_firma.close()
            firma_path = tmp_firma.name
        elif usuario and institucion_id is not None:
            try:
                contenido_firma = supabase.storage.from_(BUCKET_FIRMAS).download(
                    f"firma-{usuario}--{institucion_id}.png"
                )
                if contenido_firma:
                    tmp_firma = tempfile.NamedTemporaryFile(delete=False)
                    tmp_firma.write(contenido_firma)
                    tmp_firma.close()
                    firma_path = tmp_firma.name
            except Exception:
                pass

        if sello:
            contenido_sello = await sello.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                f"sello-{usuario}--{institucion_id}.png",
                contenido_sello,
                {"content-type": sello.content_type},
            )
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(contenido_sello)
            tmp_sello.close()
            sello_path = tmp_sello.name
        elif usuario and institucion_id is not None:
            try:
                contenido_sello = supabase.storage.from_(BUCKET_FIRMAS).download(
                    f"sello-{usuario}--{institucion_id}.png"
                )
                if contenido_sello:
                    tmp_sello = tempfile.NamedTemporaryFile(delete=False)
                    tmp_sello.write(contenido_sello)
                    tmp_sello.close()
                    sello_path = tmp_sello.name
            except Exception:
                pass

        pdf_path = generar_pdf_indicaciones(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(nombre_pdf, f, upsert=True)

        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_pdf)

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
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_indicaciones")
async def enviar_pdf_indicaciones(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
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
