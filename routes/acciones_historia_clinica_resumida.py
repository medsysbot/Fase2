# ╔══════════════════════════════════════════════════════════════════════╗
# ║   HISTORIA CLÍNICA RESUMIDA - ENDPOINTS BACKEND FASTAPI - MEDSYS    ║
# ╚══════════════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import (
    generar_pdf_historia_clinica_resumida as generar_pdf_historia_clinica_resumida_pdf,
)
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.image_utils import (
    descargar_imagen,
    eliminar_imagen,
    imagen_existe,
    guardar_imagen_temporal,
)
from utils.supabase_helper import supabase, subir_pdf

# Sobrescribimos variables con las del archivo .env
load_dotenv(override=True)
router = APIRouter()

BUCKET_PDFS = "historia-clinica-resumida"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_historia_clinica_resumida")
async def guardar_historia_clinica_resumida(
    request: Request,
    dni: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    edad: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),
    tratamiento: str = Form(...),
    observaciones: str = Form(...)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        data = {
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones,
            "institucion_id": int(institucion_id),
            "usuario_id": usuario
        }
        supabase.table("historia_clinica_resumida").insert(data).execute()
        return {"message": "Guardado exitosamente"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔═════════════════════════════════════════════════╗
# ║     GENERAR Y GUARDAR PDF HISTORIA RESUMIDA     ║
# ╚═════════════════════════════════════════════════╝
@router.post("/generar_pdf_historia_clinica_resumida")
async def generar_pdf_historia_clinica_resumida_endpoint(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    edad: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),
    tratamiento: str = Form(...),
    observaciones: str = Form(...)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        datos = {
            "nombre": f"{nombre} {apellido}".strip(),
            "dni": dni,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones
        }

        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        contenido_firma, nombre_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        contenido_sello, nombre_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)
        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = await generar_pdf_historia_clinica_resumida_pdf(
            datos,
            firma_path,
            sello_path,
        )
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("historia_clinica_resumida").update({"pdf_url": pdf_url}).eq("dni", dni).execute()
        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔════════════════════════════════════════════════════╗
# ║     ENVIAR HISTORIA CLÍNICA RESUMIDA POR CORREO    ║
# ╚════════════════════════════════════════════════════╝
@router.post("/enviar_pdf_historia_clinica_resumida")
async def enviar_pdf_historia_clinica_resumida(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Historia Clínica Resumida",
            cuerpo=f"Estimado/a {nombre}, adjuntamos su historia clínica resumida.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
