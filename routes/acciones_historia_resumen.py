# ╔════════════════════════════════════════════════════════════╗
# ║      ACCIONES BACKEND - HISTORIA CLÍNICA RESUMIDA         ║
# ╚════════════════════════════════════════════════════════════╝
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from uuid import uuid4
import os, datetime, tempfile
from utils.pdf_generator import generar_pdf_resumen
from utils.email_sender import enviar_email_con_pdf

router = APIRouter()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET = "historia-resumen"
BUCKET_FIRMAS = "firma-sello-usuarios"


# ╔════════════════════════════════════════════════════════════╗
# ║     RUTA: GENERAR Y GUARDAR HISTORIA CLÍNICA RESUMIDA      ║
# ╚════════════════════════════════════════════════════════════╝

@router.post("/generar_pdf_historia_resumen")
async def generar_historia_resumen(
    request: Request,
    paciente: str = Form(...),
    dni: str = Form(...),
    edad: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),
    tratamiento: str = Form(...),
    observaciones: str = Form(...),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        datos = {
            "paciente": paciente,
            "dni": dni,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones
        }

        # Firma y sello temporales
        firma_path = sello_path = None
        if firma:
            contenido_firma = await firma.read()
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(contenido_firma)
            tmp_firma.close()
            firma_path = tmp_firma.name
            if usuario and institucion_id is not None:
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    f"firma-{usuario}--{institucion_id}.png",
                    contenido_firma,
                    {"content-type": firma.content_type},
                )
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
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(contenido_sello)
            tmp_sello.close()
            sello_path = tmp_sello.name
            if usuario and institucion_id is not None:
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    f"sello-{usuario}--{institucion_id}.png",
                    contenido_sello,
                    {"content-type": sello.content_type},
                )
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

        # Generar PDF
        pdf_path = generar_pdf_resumen(datos, firma_path, sello_path)

        # Subir a Supabase
        nombre_archivo = f"{dni}_resumen_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET).upload(nombre_archivo, f, upsert=True)

        pdf_url = supabase.storage.from_(BUCKET).get_public_url(nombre_archivo)

        # Eliminar archivos temporales de firma y sello
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)
       
        # Guardar en Supabase DB
        supabase.table("historia_clinica_resumida").insert({
            "paciente": paciente,
            "dni": dni,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones,
            "pdf_url": pdf_url
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

# ╔════════════════════════════════════════════════════════════╗
# ║        RUTA: ENVIAR HISTORIA CLÍNICA POR CORREO            ║
# ╚════════════════════════════════════════════════════════════╝

@router.post("/enviar_pdf_historia_resumen")
async def enviar_historia_resumen(
    email: str = Form(...),
    paciente: str = Form(...),
    dni: str = Form(...)
):
    try:
        registros = supabase.table("historia_clinica_resumida").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]['pdf_url'] if registros.data else None

        if not pdf_url:
            return JSONResponse(content={"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Historia Clínica Resumida",
            cuerpo=f"Estimado/a {paciente}, adjuntamos su historia clínica.",
            url_pdf=pdf_url
        )

        return {"exito": True}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
