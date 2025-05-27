# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - BÚSQUEDA DE PACIENTES        ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_busqueda
from dotenv import load_dotenv
import os
from utils.supabase_helper import supabase, subir_pdf

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "busqueda-de-pacientes"

@router.post("/buscar_paciente")
async def buscar_paciente(request: Request, dni: str = Form(...)):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
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
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)
        supabase.table("busquedas").insert({
            "dni": dni,
            "nombre": datos["nombre"],
            "email": datos["email"],
            "telefono": datos["telefono"],
            "pdf_url": pdf_url,
            "institucion_id": institucion_id,
        }).execute()
        return JSONResponse({"exito": True, "datos": datos, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
