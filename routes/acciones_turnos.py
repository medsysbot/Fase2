# ╔════════════════════════════════════════════════╗
# ║          RUTA BACKEND - TURNOS PACIENTES      ║
# ╚════════════════════════════════════════════════╝

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from utils import generar_pdf_turno_paciente, enviar_email_con_pdf
from utils.supabase_helper import supabase, subir_pdf
from utils.image_utils import descargar_imagen, guardar_imagen_temporal
import os
import tempfile

router = APIRouter()

@router.post("/generar_pdf_turno_paciente")
async def generar_turno_paciente(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(""),
    institucion_id: int = Form(...),
    usuario_id: str = Form(...)
):
    try:
        # ═════ Validar sesión ═════
        if not institucion_id or not usuario_id:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        # ═════ Validación de campos ═════
        campos = [dni, nombre, apellido, especialidad, profesional, fecha, hora, usuario_id, institucion_id]
        if not all(c and str(c).strip() != "" for c in campos):
            return JSONResponse({"exito": False, "mensaje": "Faltan campos obligatorios."})

        # ═════ Obtener firma y sello ═════
        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"
        c_firma, n_firma = descargar_imagen(supabase, "firma-sello-usuarios", base_firma)
        c_sello, n_sello = descargar_imagen(supabase, "firma-sello-usuarios", base_sello)

        firma_path = guardar_imagen_temporal(c_firma, n_firma) if c_firma else None
        sello_path = guardar_imagen_temporal(c_sello, n_sello) if c_sello else None

        datos_pdf = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
        }
        pdf_path = generar_pdf_turno_paciente(datos_pdf, firma_path, sello_path)

        # ═════ Subir a Supabase ═════
        nombre_archivo = f"{dni}_turno.pdf"
        with open(pdf_path, "rb") as f:
            url_pdf = subir_pdf("turnos_pacientes", nombre_archivo, f)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        # ═════ Insertar en Supabase DB ═════
        supabase.table("turnos_pacientes").insert({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "pdf_url": url_pdf,
            "usuario_id": usuario_id,
            "institucion_id": institucion_id
        }).execute()

        return {"exito": True, "pdf_url": url_pdf}

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": f"Error al generar turno: {str(e)}"})

@router.post("/enviar_pdf_turno_paciente")
async def enviar_turno_paciente_por_email(
    nombre: str = Form(...),
    dni: str = Form(...),
):
    try:
        res = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = res.data.get("email") if res.data else None
        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        consulta = (
            supabase.table("turnos_pacientes")
            .select("pdf_url")
            .eq("dni", dni)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        pdf_url = consulta.data[0]["pdf_url"] if consulta.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        asunto = "Confirmación de turno médico"
        cuerpo = f"Estimado/a {nombre},\n\nAdjuntamos el PDF con los detalles de su turno médico.\n\nSaludos,\nEquipo MedSys"
        enviar_email_con_pdf(email_destino=email, asunto=asunto, cuerpo=cuerpo, pdf_url=pdf_url)

        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": f"Error al enviar el email: {str(e)}"})


@router.post("/obtener_email_paciente")
async def obtener_email_paciente(dni: str = Form(...)):
    """Devuelve el email del paciente según su DNI."""
    try:
        res = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = res.data.get("email") if res.data else None
        return {"email": email}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=500)
