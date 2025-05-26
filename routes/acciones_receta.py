from dotenv import load_dotenv
load_dotenv()

# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - RECETAS                  ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, UploadFile, File, Request
import base64
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
        contenido_firma = contenido_sello = None

        # ╔══════════════════════════════════════════════╗
        # ║                    FIRMA                     ║
        # ╚══════════════════════════════════════════════╝
        if firma:
            contenido_firma = await firma.read()
        elif usuario and institucion_id is not None:
            try:
                res_firma = (
                    supabase.table("recetas")
                    .select("firma")
                    .eq("usuario_id", usuario)
                    .eq("institucion_id", institucion_id)
                    .order("id", desc=True)
                    .limit(1)
                    .execute()
                )
                if res_firma.data:
                    contenido_firma = res_firma.data[0].get("firma")
            except Exception:
                pass

        # ╔══════════════════════════════════════════════╗
        # ║                    SELLO                     ║
        # ╚══════════════════════════════════════════════╝
        if sello:
            contenido_sello = await sello.read()
        elif usuario and institucion_id is not None:
            try:
                res_sello = (
                    supabase.table("recetas")
                    .select("sello")
                    .eq("usuario_id", usuario)
                    .eq("institucion_id", institucion_id)
                    .order("id", desc=True)
                    .limit(1)
                    .execute()
                )
                if res_sello.data:
                    contenido_sello = res_sello.data[0].get("sello")
            except Exception:
                pass

        if contenido_firma:
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(contenido_firma)
            tmp_firma.close()
            firma_path = tmp_firma.name

        if contenido_sello:
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(contenido_sello)
            tmp_sello.close()
            sello_path = tmp_sello.name

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
            "firma": contenido_firma,
            "sello": contenido_sello,
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
        res = (
            supabase.table("recetas")
            .select("firma, sello")
            .eq("usuario_id", usuario)
            .eq("institucion_id", institucion_id)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        data = res.data[0] if res.data else {}
        firma_bytes = data.get("firma") if data else None
        sello_bytes = data.get("sello") if data else None
        firma_url = (
            f"data:image/png;base64,{base64.b64encode(firma_bytes).decode()}"
            if firma_bytes else None
        )
        sello_url = (
            f"data:image/png;base64,{base64.b64encode(sello_bytes).decode()}"
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

    return {"exito": True}


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
