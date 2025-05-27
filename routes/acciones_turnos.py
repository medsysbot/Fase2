# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - TURNOS MÉDICOS            ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_turno
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.supabase_helper import supabase, subir_pdf

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "turnos-medicos"

@router.post("/generar_pdf_turno")
async def generar_turno(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(""),
    fecha: str = Form(...),
    horario: str = Form(...),
    profesional: str = Form(""),
):
    try:
        datos = {
            "nombre": nombre,
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "horario": horario,
            "profesional": profesional,
        }
        pdf_path = generar_pdf_turno(datos)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)
        supabase.table("turnos").insert({**datos, "pdf_url": pdf_url}).execute()
        return {"exito": True, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_turno")
async def enviar_pdf_turno(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
        registros = supabase.table("turnos").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]["pdf_url"] if registros.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)
        enviar_email_con_pdf(
            email_destino=email,
            asunto="Turno Médico",
            cuerpo=f"Estimado/a {nombre}, adjuntamos el turno solicitado.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
