# ╔══════════════════════════════════════════════════════════╗
# ║        ENDPOINTS PORTAL PÚBLICO - MEDSYS                ║
# ║  Todas las rutas públicas (turnos, info, landing, etc.) ║
# ╚══════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from utils.email_sender import enviar_email_con_pdf
from utils.pdf_generator import generar_pdf_turno_paciente
from utils.image_utils import guardar_imagen_temporal, descargar_imagen
from utils.supabase_helper import supabase, subir_pdf
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BUCKET_PDFS = "turnos_pacientes"
BUCKET_FIRMAS = "firma-sello-usuarios"


# ╔══════════════════════════════════════════════════════════╗
# ║   Splash de acceso público a turnos                     ║
# ╚══════════════════════════════════════════════════════════╝
@router.get("/turnos-publico", response_class=HTMLResponse)
async def splash_turnos_publico(request: Request):
    return templates.TemplateResponse("app_publico/splash_turnos_publico.html", {"request": request})

# ╔══════════════════════════════════════════════════════════╗
# ║  Formulario público para solicitar turnos médicos       ║
# ╚══════════════════════════════════════════════════════════╝
@router.get("/turnos-publico/turnos-publico", response_class=HTMLResponse)
async def formulario_turno_publico(request: Request):
    return templates.TemplateResponse("app_publico/formulario_turnos_publico.html", {"request": request})

# ╔══════════════════════════════════════════════════════════╗
# ║      Registro de turno público + email confirmación      ║
# ╚══════════════════════════════════════════════════════════╝

@router.post("/generar_pdf_turno_paciente")
async def generar_pdf_turno_paciente(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    profesional: str = Form(...),
    institucion_id: str = Form(...),
    usuario_id: str = Form(None),
):
    try:
        if not usuario_id:
            usuario_id = "bot_publico"

        datos = {
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "profesional": profesional,
        }

        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"

        firma_path = sello_path = None
        cont_firma, nombre_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        cont_sello, nombre_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)

        if cont_firma:
            firma_path = guardar_imagen_temporal(cont_firma, nombre_firma)
        if cont_sello:
            sello_path = guardar_imagen_temporal(cont_sello, nombre_sello)

        pdf_path = generar_pdf_turno_paciente(datos, firma_path, sello_path)
        filename = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, filename, f)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table("turnos_pacientes").insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "fecha": fecha,
            "hora": hora,
            "especialidad": especialidad,
            "profesional": profesional,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
            "pdf_url": pdf_url,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_turno_paciente")
async def enviar_pdf_turno_paciente(
    email: str = Form(...),
    nombre: str = Form(...),
    dni: str = Form(...),
):
    try:
        consulta = (
            supabase.table("turnos_pacientes")
            .select("*")
            .eq("dni", dni)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        datos_db = consulta.data[0] if consulta.data else None
        if not datos_db:
            return JSONResponse({"exito": False, "mensaje": "Turno no encontrado"}, status_code=404)

        usuario_id = datos_db.get("usuario_id") or "bot_publico"
        institucion_id = datos_db.get("institucion_id")

        datos_pdf = {
            "dni": datos_db["dni"],
            "especialidad": datos_db["especialidad"],
            "fecha": str(datos_db["fecha"]),
            "hora": datos_db["hora"],
            "profesional": datos_db["profesional"],
        }

        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"

        firma_path = sello_path = None
        c_firma, n_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        c_sello, n_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)

        if c_firma:
            firma_path = guardar_imagen_temporal(c_firma, n_firma)
        if c_sello:
            sello_path = guardar_imagen_temporal(c_sello, n_sello)

        pdf_path = generar_pdf_turno_paciente(datos_pdf, firma_path, sello_path)
        filename = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, filename, f)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        cuerpo = (
            f"Hola {nombre},\n\nAdjuntamos el comprobante de su turno médico.\n\nGracias por usar MEDSYS."
        )
        enviar_email_con_pdf(email_destino=email, asunto="Turno Médico - MEDSYS", cuerpo=cuerpo, url_pdf=pdf_url)

        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)

# ╔══════════════════════════════════════════════════════════╗
# ║    Espacio para futuras rutas públicas (info, landing)  ║
# ╚══════════════════════════════════════════════════════════╝

# Ejemplo:
# @router.get("/info-publica")
# async def info_publica(request: Request):
#     return templates.TemplateResponse("app_publico/info_publica.html", {"request": request})
