# ╔════════════════════════════════════════════════════════════╗
# ║           ACCIONES BACKEND - HISTORIA CLÍNICA             ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
from supabase import create_client
import tempfile
from utils.pdf_generator import generar_pdf_historia_completa
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY_SERVICE = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY_SERVICE)
BUCKET_PDFS = "pdfs"
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
        institucion_id = request.session.get("institucion_id")
        usuario = request.session.get("usuario")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión sin institución activa"}, status_code=403)

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
        if firma:
            firma_nombre = f"firma-{usuario}--{institucion_id}.png"
            contenido_firma = await firma.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                firma_nombre,
                contenido_firma,
                {"content-type": firma.content_type},
            )
            firma_url = f"{BUCKET_FIRMAS}/{firma_nombre}"
            tmp_firma = tempfile.NamedTemporaryFile(delete=False)
            tmp_firma.write(contenido_firma)
            tmp_firma.close()
            firma_path = tmp_firma.name
        elif usuario:
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

        if sello:
            sello_nombre = f"sello-{usuario}--{institucion_id}.png"
            contenido_sello = await sello.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(
                sello_nombre,
                contenido_sello,
                {"content-type": sello.content_type},
            )
            sello_url = f"{BUCKET_FIRMAS}/{sello_nombre}"
            tmp_sello = tempfile.NamedTemporaryFile(delete=False)
            tmp_sello.write(contenido_sello)
            tmp_sello.close()
            sello_path = tmp_sello.name
        elif usuario:
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
        pdf_path = generar_pdf_historia_completa(datos, firma_path, sello_path)
        filename = os.path.basename(pdf_path)

        # Subir a Supabase
        with open(pdf_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(filename, file_data, {"content-type": "application/pdf"})

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

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
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
        pdf_url = supabase.storage.from_(BUCKET_PDFS).get_public_url(filename)

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Historia Clínica Completa - MEDSYS",
            cuerpo=f"Estimado/a {nombre},\n\nAdjuntamos su historia clínica en formato PDF.\n\nSaludos,\nEquipo MEDSYS",
            url_pdf=pdf_url
        )
        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
