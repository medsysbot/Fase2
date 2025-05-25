from dotenv import load_dotenv
load_dotenv()

# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - RECETAS                  ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
import os, tempfile, datetime
from utils.pdf_generator import generar_pdf_receta
from utils.email_sender import enviar_email_con_pdf

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

        firma_path = sello_path = None

        # ╔══════════════════════════════════════════════╗
        # ║                    FIRMA                     ║
        # ╚══════════════════════════════════════════════╝
        if firma:
            contenido_firma = await firma.read()
            nombre_firma = f"firma-{usuario}--{institucion_id}.png"
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_firma,
                contenido_firma,
                {"content-type": firma.content_type},
            )
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(contenido_firma)
            tmp_firma.close()
            firma_path = tmp_firma.name
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

        # ╔══════════════════════════════════════════════╗
        # ║                    SELLO                     ║
        # ╚══════════════════════════════════════════════╝
        if sello:
            contenido_sello = await sello.read()
            nombre_sello = f"sello-{usuario}--{institucion_id}.png"
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                nombre_sello,
                contenido_sello,
                {"content-type": sello.content_type},
            )
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(contenido_sello)
            tmp_sello.close()
            sello_path = tmp_sello.name
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

        pdf_path = generar_pdf_receta(datos, firma_path, sello_path)

        nombre_archivo = f"{dni}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(pdf_path, "rb") as f:
            supabase.storage.from_(BUCKET_PDFS).upload(nombre_archivo, f, upsert=True)

        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_archivo)

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
            "pdf_url": pdf_url,
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.get("/obtener_firma_sello")
async def obtener_firma_sello(request: Request):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if not usuario or institucion_id is None:
        return JSONResponse({"exito": False, "mensaje": "Usuario no autenticado"}, status_code=403)

    firma_nombre = f"firma-{usuario}--{institucion_id}.png"
    sello_nombre = f"sello-{usuario}--{institucion_id}.png"
    firma_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(firma_nombre)
    sello_url = supabase.storage.from_(BUCKET_FIRMAS).get_public_url(sello_nombre)
    return {"firma_url": firma_url, "sello_url": sello_url}


@router.post("/eliminar_firma_sello")
async def eliminar_firma_sello(request: Request, tipo: str = Form(...)):
    usuario = request.session.get("usuario")
    institucion_id = request.session.get("institucion_id")
    if not usuario or institucion_id is None:
        return JSONResponse({"exito": False, "mensaje": "Usuario no autenticado"}, status_code=403)

    nombre_archivo = f"{tipo}-{usuario}--{institucion_id}.png"
    try:
        supabase.storage.from_(BUCKET_FIRMAS).remove(nombre_archivo)
        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_receta")
async def enviar_pdf_receta(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
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
