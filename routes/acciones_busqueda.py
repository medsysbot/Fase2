# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - BÚSQUEDA DE PACIENTES        ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_busqueda
from dotenv import load_dotenv
import os
from utils.supabase_helper import supabase

load_dotenv()
router = APIRouter()

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
            supabase.storage.from_(BUCKET_PDFS).upload(
                nombre_pdf,
                f,
                {"content-type": "application/pdf"},
            )
        pdf_obj = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_pdf)
        pdf_url = pdf_obj.get("publicUrl") if isinstance(pdf_obj, dict) else pdf_obj
        return {"exito": True, "datos": datos, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
