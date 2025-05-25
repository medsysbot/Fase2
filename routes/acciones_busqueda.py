# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - BÚSQUEDA DE PACIENTES        ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from utils.pdf_generator import generar_pdf_busqueda
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "busqueda-de-pacientes"

@router.post("/buscar_paciente")
async def buscar_paciente(dni: str = Form(...)):
    try:
        resultado = supabase.table("pacientes").select("nombres, apellido, email, telefono").eq("dni", dni).single().execute()
        if not resultado.data:
            return JSONResponse({"exito": False, "mensaje": "Paciente no encontrado"}, status_code=404)
        datos = {
            "dni": dni,
            "nombre": f"{resultado.data.get('nombres','')} {resultado.data.get('apellido','')}",
            "email": resultado.data.get('email',''),
            "telefono": resultado.data.get('telefono',''),
        }
        pdf_path = generar_pdf_busqueda(datos)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(nombre_pdf, f, upsert=True)
        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_pdf)
        return {"exito": True, "datos": datos, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
