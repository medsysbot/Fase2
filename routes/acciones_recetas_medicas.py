from dotenv import load_dotenv
# Cargamos variables de entorno de .env, priorizando sobre las ya definidas
load_dotenv(override=True)

# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - RECETAS                  ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, UploadFile, File, Request
import base64
from fastapi.responses import JSONResponse
import os, datetime
from utils.pdf_generator import generar_pdf_recetas_medicas
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import (
    descargar_imagen,
    eliminar_imagen,
    imagen_existe,
    guardar_imagen_temporal,
)

from utils.supabase_helper import supabase, SUPABASE_URL, subir_pdf

router = APIRouter()

BUCKET_PDFS = "recetas-medicas"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔═══════════════════════════════════╗
# ║        GUARDAR FORMULARIO        ║
# ╚═══════════════════════════════════╝

@router.post("/guardar_receta_medica")
async def guardar_receta_medica(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    medicamentos: str = Form(...),
    profesional: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        if not all([dni, nombre, fecha, diagnostico, medicamentos, profesional]):
            return JSONResponse({"error": "Faltan datos obligatorios"}, status_code=400)
        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            return JSONResponse({"error": "Fecha inválida"}, status_code=400)

        datos = {
            "nombre_completo": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
        }

        firma_url = sello_url = None
        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"

        # ╔══════════════════════════════════════════════╗
        # ║                    FIRMA                     ║
        # ╚══════════════════════════════════════════════╝
        contenido_firma, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_firma
        )
        if nombre_firma:
            pdf_obj = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_firma)
            firma_url = pdf_obj.get("publicUrl") if isinstance(pdf_obj, dict) else pdf_obj
        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        # ╔══════════════════════════════════════════════╗
        # ║                    SELLO                     ║
        # ╚══════════════════════════════════════════════╝
        contenido_sello, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_sello
        )
        if nombre_sello:
            pdf_obj = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_sello)
            sello_url = pdf_obj.get("publicUrl") if isinstance(pdf_obj, dict) else pdf_obj
        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        # ╔═══════════════════════════════════════╗
        # ║     GENERAR Y GUARDAR PDF RECETA     ║
        # ╚═══════════════════════════════════════╝
        pdf_path = generar_pdf_recetas_medicas(datos, firma_path, sello_path)

        nombre_archivo = f"{dni}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_archivo, f)

        supabase.table("recetas_medicas").insert({
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
            "profesional": profesional,
            "institucion_id": int(institucion_id),
            "pdf_url": pdf_url,
            "usuario_id": usuario,
        }).execute()

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        return {"pdf_url": pdf_url}

    except Exception as e:
        error_text = str(e)
        if "Duplicate" in error_text or "duplicate" in error_text:
            mensaje = "Ya existe una receta para este paciente con esos datos."
            return JSONResponse(content={"exito": False, "mensaje": mensaje}, status_code=400)
        return JSONResponse(content={"exito": False, "mensaje": error_text}, status_code=500)


# Endpoints centralizados para la carga y gestión de firma y sello.
# Esta es la única vía para que el profesional suba o reemplace las imágenes
# mediante la pantalla `firma_sello.html`.
@router.get("/obtener_firma_sello")
async def obtener_firma_sello(request: Request):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if institucion_id is None or not usuario:
        return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

    try:
        firma_bytes, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, f"firma_{usuario}_{institucion_id}"
        )
        sello_bytes, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, f"sello_{usuario}_{institucion_id}"
        )
        firma_url = (
            f"data:image/{os.path.splitext(nombre_firma)[1][1:]};base64,{base64.b64encode(firma_bytes).decode()}"
            if firma_bytes else None
        )
        sello_url = (
            f"data:image/{os.path.splitext(nombre_sello)[1][1:]};base64,{base64.b64encode(sello_bytes).decode()}"
            if sello_bytes else None
        )
        return {"firma_url": firma_url, "sello_url": sello_url}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/eliminar_firma_sello")
async def eliminar_firma_sello(request: Request, tipo: str = Form(...)):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if institucion_id is None or not usuario:
        return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

    try:
        eliminar_imagen(supabase, BUCKET_FIRMAS, f"{tipo}_{usuario}_{institucion_id}")
        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

@router.post("/subir_firma_sello")
async def subir_firma_sello(
    request: Request,
    tipo: str = Form(...),
    archivo: UploadFile = File(...),
):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if institucion_id is None or not usuario:
        return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

    try:
        contenido = await archivo.read()
        extension = os.path.splitext(archivo.filename)[1].lower()
        base_name = f"{tipo}_{usuario}_{institucion_id}"
        nombre_obj = f"{base_name}{extension}"
        if not imagen_existe(supabase, BUCKET_FIRMAS, base_name):
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_obj,
                contenido,
                {"x-upsert": "true"},
            )
        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


# ╔════════════════════════════════════════════╗
# ║      ENVIAR RECETA MÉDICA POR CORREO      ║
# ╚════════════════════════════════════════════╝
@router.post("/enviar_pdf_receta_medica")
async def enviar_pdf_receta_medica(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...),
):
    try:
        resultado = supabase.table("registro_pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        if not pdf_url:
            return JSONResponse(content={"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Receta Médica",
            cuerpo=f"Estimado/a {nombre}, adjuntamos su receta.",
            url_pdf=pdf_url
        )

        return {"exito": True}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/obtener_email_receta")
async def obtener_email_receta(dni: str = Form(...)):
    """Devuelve el email del paciente a partir de su DNI."""
    try:
        resultado = supabase.table("registro_pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None
        return {"email": email}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
