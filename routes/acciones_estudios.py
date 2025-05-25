from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from supabase import create_client
import os, asyncio, imaplib, email, re
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_PDFS = "estudios-medicos"

EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_IMAP_USER = os.getenv("EMAIL_IMAP_USER")
EMAIL_IMAP_PASSWORD = os.getenv("EMAIL_IMAP_PASSWORD")

# ╔══════════════════════════════════════════════╗
# ║   PROCESAR CORREOS Y GUARDAR EN SUPABASE     ║
# ╚══════════════════════════════════════════════╝
async def procesar_correos():
    if not (EMAIL_IMAP_USER and EMAIL_IMAP_PASSWORD):
        print("Credenciales IMAP no configuradas")
        return
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
        imap.login(EMAIL_IMAP_USER, EMAIL_IMAP_PASSWORD)
        imap.select("INBOX")
        status, mensajes = imap.search(None, "UNSEEN")
        for num in mensajes[0].split():
            status, datos = imap.fetch(num, "(RFC822)")
            mensaje = email.message_from_bytes(datos[0][1])
            fecha_email = email.utils.parsedate_to_datetime(mensaje["Date"]).date().isoformat()
            cuerpo = ""
            if mensaje.is_multipart():
                for part in mensaje.walk():
                    if part.get_content_type() == "text/plain":
                        cuerpo += part.get_payload(decode=True).decode(errors="ignore")
            else:
                cuerpo = mensaje.get_payload(decode=True).decode(errors="ignore")

            dni = re.search(r"DNI[:\s]+(\d+)", cuerpo)
            tipo = re.search(r"Tipo[:\s]+([\w\s]+)", cuerpo)
            dni = dni.group(1) if dni else None
            tipo_estudio = tipo.group(1).strip() if tipo else "desconocido"

            for part in mensaje.walk():
                if part.get_content_type() == "application/pdf":
                    pdf_data = part.get_payload(decode=True)
                    nombre_archivo = f"{dni or 'sin_dni'}_{tipo_estudio}_{fecha_email}.pdf"
                    supabase.storage.from_(BUCKET_PDFS).upload(nombre_archivo, pdf_data, {"content-type": "application/pdf"})
                    url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_archivo)
                    supabase.table("estudios").insert({
                        "dni": dni,
                        "tipo_estudio": tipo_estudio,
                        "fecha_estudio": fecha_email,
                        "url_pdf": url
                    }).execute()
            imap.store(num, '+FLAGS', '\\Seen')
        imap.logout()
    except Exception as e:
        print("Error procesando correos:", e)

async def monitor_correos():
    while True:
        await procesar_correos()
        await asyncio.sleep(300)

# ╔══════════════════════════════════════════════╗
# ║              ENDPOINTS API                   ║
# ╚══════════════════════════════════════════════╝
@router.get("/consultar_estudios/{dni}")
async def consultar_estudios(dni: str):
    res = supabase.table("estudios").select("id, tipo_estudio, fecha_estudio").eq("dni", dni).execute()
    return {"estudios": res.data}

@router.get("/obtener_estudio/{estudio_id}")
async def obtener_estudio(estudio_id: int):
    res = supabase.table("estudios").select("url_pdf").eq("id", estudio_id).single().execute()
    url = res.data.get("url_pdf") if res.data else None
    return {"url_pdf": url}


@router.get("/ver_estudio/{dni}/{tipo_estudio}")
async def ver_estudio(dni: str, tipo_estudio: str):
    nombre = f"{dni}-{tipo_estudio}.pdf".replace(" ", "_")
    try:
        supabase.storage.from_(BUCKET_PDFS).download(nombre)
    except Exception:
        return JSONResponse({"exito": False}, status_code=404)
    url = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre)
    return {"exito": True, "pdf_url": url}


@router.post("/guardar_estudio")
async def guardar_estudio(
    request: Request,
    paciente_id: int = Form(...),
    institucion_id: int = Form(...),
    tipo_estudio: str = Form(...),
    fecha: str = Form(...),
    descripcion: str = Form(""),
    archivo_pdf: UploadFile = File(None),
    pdf_url: str = Form("")
):
    try:
        pdf_url_final = pdf_url
        if archivo_pdf:
            nombre_archivo = f"{paciente_id}-{tipo_estudio}.pdf".replace(" ", "_")
            contenido = await archivo_pdf.read()
            supabase.storage.from_(BUCKET_PDFS).upload(
                nombre_archivo,
                contenido,
                {"content-type": archivo_pdf.content_type},
            )
            pdf_url_final = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre_archivo)

        supabase.table("estudios").insert({
            "paciente_id": paciente_id,
            "institucion_id": institucion_id,
            "tipo_estudio": tipo_estudio,
            "fecha": fecha,
            "descripcion": descripcion,
            "pdf_url": pdf_url_final,
        }).execute()

        return {"exito": True, "pdf_url": pdf_url_final}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

# Función para iniciar el monitor desde main
async def iniciar_monitor():
    asyncio.create_task(monitor_correos())

