from fastapi import APIRouter, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
import os, asyncio, imaplib, email, re
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv
from utils.supabase_helper import supabase, subir_pdf

# Prioriza las variables del archivo .env sobre las existentes
load_dotenv(override=True)
router = APIRouter()

BUCKET_PDFS = "estudios-medicos"

EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_IMAP_USER = os.getenv("EMAIL_IMAP_USER")
EMAIL_IMAP_PASSWORD = os.getenv("EMAIL_IMAP_PASSWORD")

# ╔══════════════════════════════════════════════╗
# ║   PROCESAR CORREOS Y GUARDAR EN SUPABASE     ║
# ╚══════════════════════════════════════════════╝
async def revisar_bandeja_email():
    """Revisar bandeja institucional y procesar adjuntos."""
    # TODO: extraer DNI y nombre del paciente de cada correo y
    # agregar el estudio de manera automática.
    pass

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
                    url = subir_pdf(BUCKET_PDFS, nombre_archivo, pdf_data)
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
        await revisar_bandeja_email()
        await asyncio.sleep(3600)

# ╔══════════════════════════════════════════════╗
# ║              ENDPOINTS API                   ║
# ╚══════════════════════════════════════════════╝
@router.get("/consultar_estudios/{dni}")
async def consultar_estudios(dni: str):
    campos = "id, tipo_estudio, fecha_estudio, descripcion, url_pdf"
    res = (
        supabase.table("estudios")
        .select(campos)
        .eq("dni", dni)
        .execute()
    )
    return {"estudios": res.data}


@router.get("/api/sugerencias_pacientes")
async def sugerencias_pacientes(q: str = ""):
    """Devuelve pacientes coincidentes para autocompletar."""
    if not q:
        return {"pacientes": []}
    try:
        consulta = supabase.table("registro_pacientes").select("dni, nombres, apellido")
        if q.isdigit():
            consulta = consulta.ilike("dni", f"{q}%")
        else:
            consulta = consulta.ilike("nombres", f"%{q}%")
        res = consulta.limit(10).execute()
        return {"pacientes": res.data}
    except Exception:
        return {"pacientes": []}

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
    pdf_obj = supabase.storage.from_(BUCKET_PDFS).get_public_url(nombre)
    url = pdf_obj.get("publicUrl") if isinstance(pdf_obj, dict) else pdf_obj
    return {"exito": True, "pdf_url": url}


@router.post("/guardar_estudio")
async def guardar_estudio(
    request: Request,
    paciente_id: int = Form(...),
    tipo_estudio: str = Form(...),
    fecha: str = Form(...),
    descripcion: str = Form(""),
    archivo_pdf: UploadFile = File(None),
    pdf_url: str = Form("")
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        pdf_url_final = pdf_url
        if archivo_pdf:
            nombre_archivo = f"{paciente_id}-{tipo_estudio}.pdf".replace(" ", "_")
            contenido = await archivo_pdf.read()
            pdf_url_final = subir_pdf(BUCKET_PDFS, nombre_archivo, contenido)

        supabase.table("estudios").insert({
            "paciente_id": paciente_id,
            "institucion_id": institucion_id,
            "tipo_estudio": tipo_estudio,
            "fecha": fecha,
            "descripcion": descripcion,
            "pdf_url": pdf_url_final,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url_final})
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

@router.post("/enviar_pdf_estudio")
async def enviar_pdf_estudio(dni: str = Form(...), estudio_id: int = Form(...)):
    """Envía por correo el PDF de un estudio al email del paciente."""
    try:
        paciente = (
            supabase.table("registro_pacientes")
            .select("nombres, apellido, email")
            .eq("dni", dni)
            .single()
            .execute()
        )
        datos = paciente.data
        if not datos or not datos.get("email"):
            return JSONResponse(
                {"exito": False, "mensaje": "Paciente sin email registrado"},
                status_code=404,
            )

        estudio = (
            supabase.table("estudios")
            .select("pdf_url, tipo_estudio")
            .eq("id", estudio_id)
            .single()
            .execute()
        )
        datos_estudio = estudio.data
        if not datos_estudio:
            return JSONResponse(
                {"exito": False, "mensaje": "Estudio no encontrado"},
                status_code=404,
            )

        enviar_email_con_pdf(
            email_destino=datos["email"],
            asunto="Estudio Médico",
            cuerpo=(
                f"Estimado/a {datos.get('nombres','')} {datos.get('apellido','')},\n"
                f"Adjuntamos su estudio de {datos_estudio.get('tipo_estudio','')}."
            ),
            url_pdf=datos_estudio.get("pdf_url"),
        )
        return {"exito": True}

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/api/enviar_estudio_email")
async def enviar_estudio_email(
    email: str = Form(...), url: str = Form(...), descripcion: str = Form("")
):
    """Envía el PDF de un estudio al email proporcionado."""
    try:
        asunto = "Estudio Médico"
        cuerpo = f"Adjuntamos el estudio: {descripcion}" if descripcion else "Adjuntamos el estudio solicitado."
        enviar_email_con_pdf(
            email_destino=email,
            asunto=asunto,
            cuerpo=cuerpo,
            url_pdf=url,
        )
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# Función para iniciar el monitor desde main
async def iniciar_monitor():
    asyncio.create_task(monitor_correos())

