# ╔════════════════════════════════════════════════════════════════════════╗
# ║     HISTORIA CLÍNICA COMPLETA - ENDPOINTS BACKEND FASTAPI - MEDSYS    ║
# ╚════════════════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_historia_clinica_completa
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.image_utils import (
    descargar_imagen,
    guardar_imagen_temporal,
)
from utils.supabase_helper import supabase, subir_pdf

# Utilizamos el .env para definir las variables necesarias
load_dotenv(override=True)
router = APIRouter()

BUCKET_PDFS = "historia_clinica_completa"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_historia_clinica_completa")
async def guardar_historia_clinica_completa(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    edad: str = Form(...),
    sexo: str = Form(...),
    dni: str = Form(...),
    domicilio: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    obra_social: str = Form(...),
    numero_afiliado: str = Form(...),
    antecedentes_personales: str = Form(...),
    antecedentes_familiares: str = Form(...),
    habitos: str = Form(...),
    enfermedades_cronicas: str = Form(...),
    cirugias: str = Form(...),
    medicacion: str = Form(...),
    estudios: str = Form(...),
    historial_tratamientos: str = Form(...),
    historial_consultas: str = Form(...)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        data = {
            "nombre": nombre,
            "apellido": apellido,
            "fecha_nacimiento": fecha_nacimiento,
            "edad": edad,
            "sexo": sexo,
            "dni": dni,
            "domicilio": domicilio,
            "telefono": telefono,
            "email": email,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
            "antecedentes_personales": antecedentes_personales,
            "antecedentes_familiares": antecedentes_familiares,
            "habitos": habitos,
            "enfermedades_cronicas": enfermedades_cronicas,
            "cirugias": cirugias,
            "medicacion": medicacion,
            "estudios": estudios,
            "historial_tratamientos": historial_tratamientos,
            "historial_consultas": historial_consultas,
            "institucion_id": int(institucion_id),
            "usuario_id": usuario
        }
        supabase.table("historia_clinica_completa").insert(data).execute()
        return {"message": "Guardado exitosamente"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔═════════════════════════════════════════════════════════╗
# ║     GENERAR Y GUARDAR PDF HISTORIA CLÍNICA COMPLETA     ║
# ╚═════════════════════════════════════════════════════════╝
@router.post("/generar_pdf_historia_clinica_completa")
async def generar_pdf_historia_clinica_completa(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        datos = {
            "nombre": f"{nombre} {apellido}".strip(),
            "dni": dni
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

        pdf_path = await generar_pdf_historia_clinica_completa(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        supabase.table("historia_clinica_completa").update({"pdf_url": pdf_url}).eq("dni", dni).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

# ╔═════════════════════════════════════════════════════════╗
# ║     ENVIAR HISTORIA CLÍNICA COMPLETA POR CORREO         ║
# ╚═════════════════════════════════════════════════════════╝
@router.post("/enviar_pdf_historia_clinica_completa")
async def enviar_pdf_historia_clinica_completa(
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
            asunto="Historia Clínica Completa",
            cuerpo=f"Estimado/a {nombre}, adjuntamos su historia clínica completa.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
