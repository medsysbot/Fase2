from dotenv import load_dotenv
load_dotenv()

# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - RECETAS                  ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, UploadFile, File, Request
import base64
from fastapi.responses import JSONResponse
from supabase import create_client
import os, datetime
from utils.pdf_generator import generar_pdf_receta
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import (
    descargar_imagen,
    eliminar_imagen,
    validar_imagen,
    obtener_mime,
    imagen_existe,
)

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "recetas-medicas"
BUCKET_FIRMAS = "firma-sello-usuarios"

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
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        datos = {
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
        }

        firma_url = sello_url = None
        contenido_firma = contenido_sello = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"

        # ╔══════════════════════════════════════════════╗
        # ║                    FIRMA                     ║
        # ╚══════════════════════════════════════════════╝
        if firma:
            contenido_firma = await firma.read()
            ext_firma = os.path.splitext(firma.filename)[1].lower()
            if not validar_imagen(contenido_firma, ext_firma):
                return JSONResponse(
                    {"exito": False, "mensaje": "Formato de imagen no soportado para firma o sello"},
                    status_code=400,
                )
            nombre_firma = f"{base_firma}{ext_firma}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_firma):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_firma,
                    contenido_firma,
                    {"content-type": obtener_mime(contenido_firma)},
                )
            firma_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_firma)
            print("URL firma:", firma_url)
        elif usuario and institucion_id is not None:
            contenido_firma, nombre_firma = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_firma
            )
            if nombre_firma:
                firma_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_firma)
                print("URL firma:", firma_url)

        # ╔══════════════════════════════════════════════╗
        # ║                    SELLO                     ║
        # ╚══════════════════════════════════════════════╝
        if sello:
            contenido_sello = await sello.read()
            ext_sello = os.path.splitext(sello.filename)[1].lower()
            if not validar_imagen(contenido_sello, ext_sello):
                return JSONResponse(
                    {"exito": False, "mensaje": "Formato de imagen no soportado para firma o sello"},
                    status_code=400,
                )
            nombre_sello = f"{base_sello}{ext_sello}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_sello):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_sello,
                    contenido_sello,
                    {"content-type": obtener_mime(contenido_sello)},
                )
            sello_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_sello)
            print("URL sello:", sello_url)
        elif usuario and institucion_id is not None:
            contenido_sello, nombre_sello = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_sello
            )
            if nombre_sello:
                sello_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(nombre_sello)
                print("URL sello:", sello_url)

        pdf_path = generar_pdf_receta(datos, firma_url, sello_url)

        nombre_archivo = f"{dni}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        # Verificar si ya existe una receta con el mismo nombre
        existentes = supabase.storage.from_(BUCKET_PDFS).list()
        if any(obj.get("name") == nombre_archivo for obj in existentes):
            mensaje = "Ya existe una receta para este paciente con esos datos."
            return JSONResponse(content={"exito": False, "mensaje": mensaje}, status_code=400)

        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(
                nombre_archivo,
                f,
                {"content-type": "application/pdf"},
            )

        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_archivo)

        supabase.table("recetas").insert({
            "nombre": nombre,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "medicamentos": medicamentos,
            "pdf_url": pdf_url,
            "usuario_id": usuario,
            "institucion_id": institucion_id,
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}

    except Exception as e:
        error_text = str(e)
        if "Duplicate" in error_text or "duplicate" in error_text:
            mensaje = "Ya existe una receta para este paciente con esos datos."
            return JSONResponse(content={"exito": False, "mensaje": mensaje}, status_code=400)
        return JSONResponse(content={"exito": False, "mensaje": error_text}, status_code=500)


@router.get("/obtener_firma_sello")
async def obtener_firma_sello(request: Request):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if not usuario or institucion_id is None:
        return JSONResponse({"exito": False, "mensaje": "Usuario no autenticado"}, status_code=403)

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
    if not usuario or institucion_id is None:
        return JSONResponse({"exito": False, "mensaje": "Usuario no autenticado"}, status_code=403)

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
    if not usuario or institucion_id is None:
        return JSONResponse({"exito": False, "mensaje": "Usuario no autenticado"}, status_code=403)

    try:
        contenido = await archivo.read()
        extension = os.path.splitext(archivo.filename)[1].lower()
        if not validar_imagen(contenido, extension):
            return JSONResponse(
                {"exito": False, "mensaje": "Formato de imagen no soportado para firma o sello"},
                status_code=400,
            )
        base_name = f"{tipo}_{usuario}_{institucion_id}"
        nombre_obj = f"{base_name}{extension}"
        if not imagen_existe(supabase, BUCKET_FIRMAS, base_name):
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_obj,
                contenido,
                {"content-type": obtener_mime(contenido)},
            )
        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_receta")
async def enviar_pdf_receta(nombre: str = Form(...), dni: str = Form(...)):
    try:
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        registros = supabase.table("recetas").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]['pdf_url'] if registros.data else None

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
        resultado = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = resultado.data.get("email") if resultado.data else None
        return {"email": email}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
