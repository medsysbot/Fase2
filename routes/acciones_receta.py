from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from uuid import uuid4
import os, tempfile, datetime
from utils.pdf_generator import generar_pdf_receta
from utils.email_sender import enviar_email_con_pdf

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET = "recetas"

@router.post("/generar_pdf_receta")
async def generar_receta(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    medicamentos: str = Form(...),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None)
):
    try:
        datos = {
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
        }

        firma_path = sello_path = None
        if firma:
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(await firma.read())
            tmp_firma.close()
            firma_path = tmp_firma.name

        if sello:
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(await sello.read())
            tmp_sello.close()
            sello_path = tmp_sello.name

        pdf_path = generar_pdf_receta(datos, firma_path, sello_path)

        nombre_archivo = f"{dni}_receta_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET).upload(nombre_archivo, f, upsert=True)

        pdf_url = supabase.storage.from_(BUCKET).get_public_url(nombre_archivo)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("recetas").insert({
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
            "pdf_url": pdf_url
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
