# ╔════════════════════════════════════════════════════════════╗
# ║           ACCIONES BACKEND - HISTORIA CLÍNICA             ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
from utils.pdf_generator import generar_pdf_historia_completa
from utils.email_sender import enviar_email_con_pdf
from utils.image_utils import (
    guardar_imagen_temporal,
    descargar_imagen,
    imagen_existe,
)
from utils.supabase_helper import supabase, SUPABASE_URL, subir_pdf
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Configuración Supabase
BUCKET_PDFS = "historia-completa"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ╔══════════════════════════════════════════════╗
# ║      REGISTRAR HISTORIA CLÍNICA Y GENERAR PDF ║
# ╚══════════════════════════════════════════════╝
@router.post("/generar_pdf_historia_completa")
async def generar_pdf_historia_completa(
    request: Request,
    nombre: str = Form(...),
    fecha_nacimiento: str = Form(...),
    edad: str = Form(...),
    sexo: str = Form(...),
    dni: str = Form(...),
    domicilio: str = Form(""),
    telefono: str = Form(""),
    email: str = Form(""),
    obra_social: str = Form(""),
    numero_afiliado: str = Form(""),
    antecedentes_personales: str = Form(""),
    antecedentes_familiares: str = Form(""),
    habitos: str = Form(""),
    enfermedades_cronicas: str = Form(""),
    cirugias: str = Form(""),
    medicacion: str = Form(""),
    estudios: str = Form(""),
    historial_tratamientos: str = Form(""),
    historial_consultas: str = Form(""),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None)
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        datos = {
            "nombre": nombre,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "edad": edad,
            "sexo": sexo,
            "telefono": telefono,
            "email": email,
            "domicilio": domicilio,
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
        }
        firma_url = ""
        sello_url = ""
        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        if firma:
            contenido_firma = await firma.read()
            ext_firma = os.path.splitext(firma.filename)[1].lower()
            nombre_firma = f"{base_firma}{ext_firma}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_firma):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_firma,
                    contenido_firma,
                    {"x-upsert": "true"},
                )
            firma_url = f"{BUCKET_FIRMAS}/{nombre_firma}"
        elif usuario:
            contenido_firma, nombre_firma = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_firma
            )
        if sello:
            contenido_sello = await sello.read()
            ext_sello = os.path.splitext(sello.filename)[1].lower()
            nombre_sello = f"{base_sello}{ext_sello}"
            if not imagen_existe(supabase, BUCKET_FIRMAS, base_sello):
                supabase.storage.from_(BUCKET_FIRMAS).upload(
                    nombre_sello,
                    contenido_sello,
                    {"x-upsert": "true"},
                )
            sello_url = f"{BUCKET_FIRMAS}/{nombre_sello}"
        elif usuario:
            contenido_sello, nombre_sello = descargar_imagen(
                supabase, BUCKET_FIRMAS, base_sello
            )

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        pdf_path = generar_pdf_historia_completa(datos, firma_path, sello_path)
        filename = os.path.basename(pdf_path)

        # Subir a Supabase
        with open(pdf_path, "rb") as file_data:
            public_url = subir_pdf(BUCKET_PDFS, filename, file_data)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)
        # Guardar en base
        supabase.table("historia_clinica_completa").insert({
            "paciente_id": dni,
            "nombre": nombre,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "edad": edad,
            "sexo": sexo,
            "telefono": telefono,
            "email": email,
            "domicilio": domicilio,
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
            "institucion_id": institucion_id,
            "firma_url": firma_url,
            "sello_url": sello_url
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ╔══════════════════════════════════════════════╗
# ║             ENVIAR PDF POR EMAIL             ║
# ╚══════════════════════════════════════════════╝
@router.post("/enviar_pdf_historia_completa")
async def enviar_pdf_historia_completa(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
        safe_name = nombre.strip().replace(" ", "_")
        filename = f"historia_completa_{safe_name}_{dni}.pdf"
        pdf_obj = supabase.storage.from_(BUCKET_PDFS).get_public_url(filename)
        pdf_url = pdf_obj.get("publicUrl") if isinstance(pdf_obj, dict) else pdf_obj

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Historia Clínica Completa - MEDSYS",
            cuerpo=f"Estimado/a {nombre},\n\nAdjuntamos su historia clínica en formato PDF.\n\nSaludos,\nEquipo MEDSYS",
            url_pdf=pdf_url
        )
        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
